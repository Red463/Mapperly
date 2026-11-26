"""Try touching native bridge components as one certified collision surface.

Bounds only discover clusters. Every emitted walking segment still needs exact
native collision-floor support, width, clearance and independently dry handoffs.
"""
from pathlib import Path
import csv,hashlib,itertools,json,math
from bridge_geometry import Reader,placed,ORIGIN
from build_bridge_expanded import extract,atomic_json
from build_southfury_bridge import runtime
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT.parent/'output/bridges-and-crossings-70959';manifest=json.loads((ROOT/'tools/data/bridges-and-crossings-manifest.json').read_text());assets=json.loads((out/'assets.json').read_text())
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']if z.get('type')in(3,6)and 'wdt'in z and z['id']!=2665};wdts={z['terrainMap']:z['wdt']for z in zones.values()}
    rows=[p for p in manifest['candidates']if p['map']in wdts and 'asset-path'in p['reasons']and not any(w in p['assetPath'].lower()for w in('brazier','lamp','torch','banner','lantern'))]
    bounds={};parent={p['key']:p['key']for p in rows}
    for p in rows:
        if p['kind']=='wmo':
            b=p['bounds'];bounds[p['key']]=[ORIGIN-b[5],ORIGIN-b[3],b[1],ORIGIN-b[2],ORIGIN-b[0],b[4]]
        else:
            b=assets['m2:'+str(p['fdid'])].get('bounds')
            if not b:continue
            vs=[placed(v,p)for v in itertools.product(*[(b[k],b[k+3])for k in range(3)])]
            bounds[p['key']]=[min(v[k]for v in vs)for k in range(3)]+[max(v[k]for v in vs)for k in range(3)]
    def root(key):
        while parent[key]!=key:parent[key]=parent[parent[key]];key=parent[key]
        return key
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            if a['map']!=b['map']or a['key']not in bounds or b['key']not in bounds:continue
            x,y=bounds[a['key']],bounds[b['key']]
            gap=math.sqrt(sum(max(x[k]-y[k+3],y[k]-x[k+3],0)**2 for k in range(3)))
            if gap<=2:parent[root(b['key'])]=root(a['key'])
    clusters={}
    for p in rows:clusters.setdefault(root(p['key']),[]).append(p)
    clusters=[c for c in clusters.values()if len(c)>1 and any(p['sourceStatus']!='certified-corridor'for p in c)]
    snapshot=ROOT.parent/'output/forever-datamine-70959';db=snapshot/'terrain-research/ashenvale/raw/dbfilesclient'
    areas={int(r['ID']):r for r in csv.DictReader((db/'areatable.csv').open(encoding='utf-8-sig'))};owners={int(r['AreaID']):int(r['UiMapID'])for r in csv.DictReader((db/'uimapassignment.csv').open(encoding='utf-8-sig'))if int(r['UiMapID'])in zones and int(r['AreaID'])}
    def owner(area):
        seen=set()
        while area and area not in seen:
            if area in owners:return owners[area]
            seen.add(area);area=int(areas.get(area,{}).get('ParentAreaID',0))
    reader=Reader(snapshot);lua=runtime()
    for f in ['Data/Water.lua','Water.lua']:lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text())
    proofs=[];report=[]
    admission={str(p.relative_to(ROOT))if p.is_relative_to(ROOT)else str(p.relative_to(snapshot)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [db/'areatable.csv',db/'uimapassignment.csv']+[ROOT/n for n in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/Water.lua','Terrain.lua','Water.lua']]}
    for components in clusters:
        components=sorted(components,key=lambda p:p['key']);keys=[p['key']for p in components];key='compound:'+hashlib.sha256('|'.join(keys).encode()).hexdigest()[:16]
        p=dict(components[0],key=key,components=components,assetName='Composite native bridge')
        row=dict(key=key,members=keys,status='unresolved')
        try:
            if len(components)>256:raise ValueError('Large multi-bridge compound requires selected subclusters')
            reader.used={};sampler=reader.sampler(p['map'],wdts[p['map']]);proof=extract(reader,p,sampler,zones,owner,lua,'compound')
            proof['provenance']['admissionSourcesSha256']=admission;proofs.append(proof);row.update(status='floor-validated',corridor=proof['corridorID'])
        except (ValueError,KeyError)as e:row['reason']=str(e)
        report.append(row);print(row,flush=True)
    atomic_json(ROOT/'tools/data/native-bridge-compound-70959.json',proofs,compact=True);atomic_json(out/'compound-validation.json',report)

if __name__=='__main__':main()
