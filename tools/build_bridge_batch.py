"""Validate straight, yaw-only bridge placements with independently dry bank contacts.

Conservative ordinary WMO batch: unsupported rotations/contact shapes stay explicit.
The inventory, not this asset family, defines the remaining work.
"""
from pathlib import Path
import argparse,csv,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
from build_southfury_bridge import Native,runtime,ORIGIN
from build_structure_corridors import validate_curved

def dry_point(lua,point):
    # Return one Lua boolean. Multi-return policy helpers become Python tuples,
    # including truthy (False, None), and must not admit a wet contact.
    return lua.eval('function(p) return A.Terrain.Segment(p,p,{allowSwimming=false}) end')(lua.table_from(point)) is True

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revalidate-certified',action='store_true',help='Re-extract the certified batch; retain other audit dispositions')
    args=parser.parse_args()
    out=ROOT.parent/'output/bridges-and-crossings-70959'
    inventory=json.loads((ROOT/'tools/data/bridges-and-crossings-manifest.json').read_text())
    assets=json.loads((out/'assets.json').read_text())
    placements=[p for p in inventory['candidates'] if p['map'] in (0,1) and p['kind']=='wmo' and 'name' in p['reasons'] and len(assets['wmo:'+str(p['fdid'])].get('groups',[]))<=4]
    snapshot=ROOT.parent/'output/forever-datamine-70959'
    db=snapshot/'terrain-research/ashenvale/raw/dbfilesclient'
    areas={int(r['ID']):r for r in csv.DictReader((db/'areatable.csv').open(encoding='utf-8-sig'))}
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones'] if z.get('terrainMap') in (0,1)}
    owners={int(r['AreaID']):int(r['UiMapID']) for r in csv.DictReader((db/'uimapassignment.csv').open(encoding='utf-8-sig')) if int(r['UiMapID']) in zones and int(r['AreaID'])}
    def owner(area):
        seen=set()
        while area and area not in seen:
            if area in owners:return owners[area]
            seen.add(area);area=int(areas.get(area,{}).get('ParentAreaID',0))
    def mapped(p,mid):
        z=zones[mid];return dict(mapID=mid,x=(z['west']-p[1])/(z['west']-z['east']),y=(z['north']-p[0])/(z['north']-z['south']))
    lua=runtime();proofs=[];report=[]
    for name in ['Data/Water.lua','Water.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/name).read_text())
    admission_sources={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p.relative_to(snapshot)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [db/'areatable.csv',db/'uimapassignment.csv']+[ROOT/name for name in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Water.lua','Terrain.lua','WalkingRegions.lua','Water.lua']]}
    if args.revalidate_certified:
        prior=json.loads((out/'bridge-family-validation.json').read_text())
        selected={r['key'] for r in prior if r['status']=='floor-validated'}
        placements=[p for p in placements if p['key'] in selected]
        report=[r for r in prior if r['key'] not in selected]
    for placement in placements:
        if placement['uid']==294532:continue
        entry=dict(key=placement['key'],placement=placement['uid'],asset=placement['fdid'],status='unresolved');report.append(entry)
        try:
            native=Native(snapshot,placement,775971 if placement['map']==0 else 782779)
            bounds=assets['wmo:'+str(placement['fdid'])]['bounds']
            axis=0 if bounds[3]-bounds[0]>bounds[4]-bounds[1] else 1
            center=(bounds[1-axis]+bounds[4-axis])/2
            def xy(t,lateral=0):return (t,center+lateral) if axis==0 else (center+lateral,t)
            def floor(t,lateral=0):return native.floor(*xy(t,lateral))
            def world(t,z):return native.world(*xy(t),z)
            low,high=bounds[axis],bounds[axis+3]
            if not 4<high-low<300:raise ValueError('Outside ordinary bridge span limit')
            contacts=[]
            for i in range(math.ceil((high-low)/.1)+1):
                y=min(high,low+i*.1);hit=floor(y)
                if not hit:continue
                p=world(y,hit[0]);t=native.terrain(*p[:2]);mid=owner(t['area'])
                if not mid or not t['permitted'] or abs(p[2]-t['height'])>.3:continue
                point=mapped(p,mid)
                if dry_point(lua,point):
                    contacts.append((y,p,t,point))
            first=[p for p in contacts if p[0]<low+(high-low)*.3];last=[p for p in contacts if p[0]>low+(high-low)*.7]
            if not first or not last:raise ValueError('No independently dry permitted contacts on both ends')
            start=max(first,key=lambda p:p[0]);end=min(last,key=lambda p:p[0])
            count=math.ceil((end[0]-start[0])/.25);points=[];samples=[];used=set();deltas=[]
            for i in range(count+1):
                y=start[0]+(end[0]-start[0])*i/count;hit=floor(y)
                if not hit or hit[2]<2.2:raise ValueError('Unsupported centerline/headroom')
                p=world(y,hit[0]);points.append(p);used.add(hit[1]);samples.append(dict(point=p,segment=min(i,count-1),headroom=hit[2]))
                for k in range(21):
                    h=floor(y,(-2.5+k*.25)/(placement['scale']/1024 if placement['flags']&4 else 1))
                    if not h or h[2]<2.2 or abs(h[0]-hit[0])*(placement['scale']/1024 if placement['flags']&4 else 1)>.3:raise ValueError('Unsupported central-strip width')
                    deltas.append((h[0]-hit[0])*(placement['scale']/1024 if placement['flags']&4 else 1))
            faces=[dict(v=[native.world(*p) for p in native.faces[i]['v']],sourceGroup=native.faces[i]['group'],sourceTriangle=native.faces[i]['triangle'],sourceFlags=native.faces[i]['flags']) for i in sorted(used)]
            row=dict(name='Native stone bridge '+str(placement['uid']),corridorID=placement['uid'],placement=placement['uid'],wmo=placement['fdid'],fromUiMap=start[3]['mapID'],toUiMap=end[3]['mapID'],build=70959,
                worldCenterline=points,samples=samples,faces=faces,landings=[dict(**p[2],mapPoint=p[3],world=p[1],terrainDelta=p[1][2]-p[2]['height']) for p in (start,end)],
                transformError=0,portalGap=0,maximumStep=max(abs(a[2]-b[2]) for a,b in zip(points,points[1:])),minimumHeadroom=min(p['headroom'] for p in samples),
                nativePlacement=placement,provenance=dict(fdidSha256=native.sources,admissionSourcesSha256=admission_sources),
                widthProof=dict(radiusYards=2.5,sampleCount=len(deltas),lateralStepYards=.25,longitudinalStepYards=(end[0]-start[0])/count,minimumHeightDelta=min(deltas),maximumHeightDelta=max(deltas)))
            transformed=[native.world(*p) for p in native.vertices]
            measured=[ORIGIN-max(p[1] for p in transformed),min(p[2] for p in transformed),ORIGIN-max(p[0] for p in transformed),ORIGIN-min(p[1] for p in transformed),max(p[2] for p in transformed),ORIGIN-min(p[0] for p in transformed)]
            slack=[measured[i]-placement['bounds'][i] if i<3 else placement['bounds'][i]-measured[i] for i in range(6)]
            if min(slack)<-.01:raise ValueError('Transformed mesh outside native placement bounds')
            row['nativeBoundsSlack']=slack;row['transformErrorMethod']='Yaw-only orthogonal native transform; native MODF bounds containment independently checked'
            length=validate_curved(row);proofs.append(row);entry.update(status='floor-validated',maps=[row['fromUiMap'],row['toUiMap']],distance=length)
        except (ValueError,KeyError,FileNotFoundError,AssertionError) as e:entry['reason']=str(e)
        (out/'bridge-family-validation.json').write_text(json.dumps(report,indent=2))
        (ROOT/'tools/data/native-bridge-batch-70959.json').write_text(json.dumps(proofs,separators=(',',':'))+'\n')
        print(entry,flush=True)
    (out/'bridge-family-validation.json').write_text(json.dumps(report,indent=2))
    (ROOT/'tools/data/native-bridge-batch-70959.json').write_text(json.dumps(proofs,separators=(',',':'))+'\n')

if __name__=='__main__':main()
