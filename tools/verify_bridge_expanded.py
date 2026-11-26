"""Independently re-probe emitted bridge floors and native liquid clearance."""
from pathlib import Path
import argparse,hashlib,json,math
from bridge_geometry import Reader,placement_error
from build_bridge_batch import dry_point
from build_southfury_bridge import runtime
from build_bridge_expanded import atomic_json
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--file',default='native-bridge-expanded-70959.json');parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--only',help='Re-probe one placement and preserve all other proofs');args=parser.parse_args()
    out=ROOT.parent/'output/bridges-and-crossings-70959';path=ROOT/'tools/data'/args.file
    proofs=json.loads(path.read_text());reader=Reader(ROOT.parent/'output/forever-datamine-70959')
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
    paths_path=out/'asset-paths.json';names=json.loads(paths_path.read_text())
    lua=runtime()
    for f in ['Data/Water.lua','Water.lua']:lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text())
    accepted=[];results=[]
    if args.only and not any(row.get('placementKey')==args.only for row in proofs):raise ValueError('Unknown placement')
    for row in proofs:
        if args.only and row.get('placementKey')!=args.only:
            accepted.append(row);continue
        p=dict(row['nativePlacement']);p.setdefault('kind','wmo');p.setdefault('map',zones[row['fromUiMap']]['terrainMap']);key=row.get('placementKey',f"{p['map']}:{p['kind']}:{p['uid']}")
        reader.used={};sampler=reader.sampler(p['map'],zones[row['fromUiMap']]['wdt']);result=dict(corridor=row['corridorID'],key=key)
        try:
            mesh,asset,slack=reader.mesh(p,sampler,p.get('selectedPart'))
            row['transformError']=placement_error(asset['vertices'],p)
            if row['transformError']>.01:raise ValueError('Placement numerical roundtrip failed')
            points=row['worldCenterline']
            for index,landing in enumerate(row['landings']):
                if not dry_point(lua,landing['mapPoint']):raise ValueError('Dry handoff rejected by runtime mask')
                if 'stripContacts' in landing:
                    a,b=points[:2] if index==0 else points[-2:]
                    span=math.dist(a[:2],b[:2]);dn,de=(b[0]-a[0])/span,(b[1]-a[1])/span
                    center=a if index==0 else b
                    samples=landing['stripContacts'];offsets=[-.5,-.25,0,.25,.5]
                    if [s['offsetYards'] for s in samples]!=offsets:raise ValueError('Incomplete chasm bridge landing strip')
                    zone=zones[landing['mapPoint']['mapID']]
                    for contact,offset in zip(samples,offsets):
                        north,east=center[0]-de*offset,center[1]+dn*offset
                        ground=reader.terrain(sampler,north,east);hit=mesh.floor(north,east,near=center[2])
                        if not hit or hit[2]<2.2 or math.dist([north,east,hit[0]],contact['world'])>.02:
                            raise ValueError('Chasm bridge landing strip failed native floor re-probe')
                        q=dict(mapID=zone['id'],x=(zone['west']-east)/(zone['west']-zone['east']),y=(zone['north']-north)/(zone['north']-zone['south']))
                        if not ground['permitted'] or abs(hit[0]-ground['height'])>.3 or not dry_point(lua,q):
                            raise ValueError('Chasm bridge landing strip failed dry ground re-probe')
            radius=row['widthProof']['radiusYards'];water_span=0.;maximum_water=0.
            for i,point in enumerate(points):
                floor=mesh.floor(*point[:2],near=point[2])
                if not floor or abs(floor[0]-point[2])>.02 or floor[2]<2.2:raise ValueError('Native floor re-probe failed')
                if i and mesh.gap(points[i-1],point)>.03:raise ValueError('Native interval re-probe failed')
                before,after=points[max(0,i-1)],points[min(len(points)-1,i+1)];span=math.dist(before[:2],after[:2])
                if span<1e-8:raise ValueError('Degenerate floor direction')
                dn,de=(after[0]-before[0])/span,(after[1]-before[1])/span
                for k in range(round(2*radius/.25)+1):
                    offset=-radius+k*.25;h=mesh.floor(point[0]-de*offset,point[1]+dn*offset,near=point[2])
                    if not h or h[2]<2.2 or abs(h[0]-point[2])>.3:raise ValueError('Native width re-probe failed')
                ground=reader.terrain(sampler,*point[:2])
                if ground['liquid']:
                    if ground['liquidHigh'] is None or not math.isfinite(ground['liquidHigh'])or point[2]<ground['liquidHigh']+.1:raise ValueError('Deck not proven above native liquid surface')
                    if i:water_span+=math.dist(points[i-1][:2],point[:2]);maximum_water=max(maximum_water,water_span)
                else:water_span=0.
            source_path=names.get(str(row.get('model')or row['wmo']),'')
            named=any(w in source_path.lower()for w in('bridge','viaduct','causeway'))and not any(w in source_path.lower()for w in('brazier','torch','lamp','banner','lantern'))
            row['assetPath']=source_path
            row['isBridgeAsset']=bool(p.get('selectedPart'))or named or maximum_water>=4
            row['classificationEvidence']='native-water-crossing'if maximum_water>=4 and not named else 'selected-native-bridge-component'if p.get('selectedPart') else 'asset-path'if named else 'unclassified-floor'
            row['maximumLiquidSpan']=maximum_water;row['verificationRevision']=3
            row['provenance']['fdidSha256'].update(reader.used)
            row['provenance']['assetPathsSha256']=hashlib.sha256(paths_path.read_bytes()).hexdigest()
            accepted.append(row);result['status']='verified'
        except (ValueError,KeyError)as error:result.update(status='rejected',reason=str(error))
        results.append(result);print(result,flush=True)
    if not args.check_only:atomic_json(path,accepted,compact=True)
    suffix='-'+args.only.replace(':','-') if args.only else ''
    atomic_json(out/(path.stem+suffix+'-reprobe.json'),results)
    if args.check_only and len(accepted)!=len(proofs):raise SystemExit('Existing bridge proof failed native re-probe')
    print('Verified',sum(r['status']=='verified' for r in results),'of',len(results),'probed corridors')

if __name__=='__main__':main()
