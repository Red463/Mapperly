"""Inventory pinned client placements and crossing evidence; never grant routing permission.

All native maps are enumerated, including instances/test maps. Read-only CASC;
restartable extraction cache outside the addon. Missing assets remain explicit.
"""
from pathlib import Path
import argparse, collections, csv, hashlib, json, math, struct, sys
from audit_crossing_approaches import verify_inventory
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/roads'))
from local_casc import LocalCasc
from build_southfury_bridge import chunks
ORIGIN=32*1600/3

def placement_key(map_id,kind,uid):return f'{map_id}:{kind}:{uid}'

def candidate_reasons(asset):
    result=[]
    if asset.get('roadWaterOverlap'):result.append('road-water-overlap')
    if any(word in asset.get('name','').lower() for word in ('bridge','viaduct','causeway')):result.append('name')
    if any(word in asset.get('path','').lower() for word in ('bridge','viaduct','causeway')):result.append('asset-path')
    b=asset.get('bounds')
    if b:
        width,length=sorted((b[3]-b[0],b[4]-b[1]))
        if length>=15 and width>0 and length/width>=2.5 and b[5]-b[2]<length:result.append('elongated-geometry')
    return result

def disposition(asset):return 'unresolved' if asset.get('error') else 'candidate'

def non_walking_inventory():
    """Account for existing native travel records without granting ground access."""
    rows=[];excluded=[]
    for filename,field in [('native-transports-70959.json','links'),('native-local-transports-70959.json','links'),('native-tram-service-70959.json','edges'),('native-tram-portals-70959.json','portals')]:
        path=ROOT/'tools/data'/filename;raw=path.read_bytes();source=json.loads(raw);sha=hashlib.sha256(raw).hexdigest()
        for record in source[field]:
            portal=field=='portals';transport='fromStop'in record
            if transport:
                start={k:record['fromStop'].get(k)for k in ('name','mapID','continent','position','approach')}
                end={k:record['toStop'].get(k)for k in ('name','mapID','continent','position','approach')}
            elif portal:start=dict(triggerID=record['triggerID']);end=record['destination']
            else:start=record['a'];end=record['b']
            rows.append(dict(id='portal:tram:'+str(record['triggerID'])if portal else record['id'],
                kind='portal'if portal else record['kind'],name=record.get('name',record.get('route')),
                source=filename,sourceSha256=sha,**{'from':start,'to':end},
                status='native-portal-destination-record'if portal else'existing-native-transport-record',
                direction='directed',walkingPermission=False,liveStatus='not-tested',
                limitations='Portal trigger destination only; not an ordinary ground connector.'if portal else'Existing travel mechanism and timing/boarding assumptions apply.'))
        for record in source.get('excluded',[]):
            excluded.append(dict(source=filename,sourceSha256=sha,record=record,
                status='superseded-by-native-tram-service'if filename=='native-local-transports-70959.json'and record.get('kind')=='tram'else'excluded-from-native-service-links'))
    return rows,excluded

def overlap_detector(zones):
    """Discovery only: collision-sized placed bounds containing road and liquid pixels."""
    sys.path.insert(0,str(ROOT/'.test-deps'))
    from PIL import Image
    layers=[]
    for z in zones:
        if z.get('type') not in (3,6):continue
        road=ROOT.parent/f"output/road-overlays-70959/{z['id']}-mask.png"
        ground=ROOT.parent/f"output/terrain-overlays-70959/{z['id']}.png"
        if road.exists() and ground.exists():layers.append((z,Image.open(road).convert('L'),Image.open(ground).convert('L')))
    def hit(q,asset):
        if q.get('kind')=='m2' and not asset.get('collisionTriangles'):return False
        b=q.get('bounds') if q.get('kind')=='wmo' else asset.get('bounds')
        if not b:return False
        if q['kind']=='wmo':
            north,east=ORIGIN-(b[2]+b[5])/2,ORIGIN-(b[0]+b[3])/2
            width,height=b[3]-b[0],b[5]-b[2]
        else:
            north,east=ORIGIN-q['pos'][2],ORIGIN-q['pos'][0]
            width=height=max(b[3]-b[0],b[4]-b[1])*q['scale']/1024
        if not 4<=max(width,height)<=300:return False
        for z,road,ground in layers:
            if z['terrainMap']!=q['map'] or not z['east']<=east<=z['west'] or not z['south']<=north<=z['north']:continue
            wet=track=False
            for i in (-.5,0,.5):
                for j in (-.5,0,.5):
                    x=(z['west']-east-i*width)/(z['west']-z['east']);y=(z['north']-north-j*height)/(z['north']-z['south'])
                    if not 0<=x<1 or not 0<=y<1:continue
                    wet=wet or ground.getpixel((int(x*ground.width),int(y*ground.height)))==128
                    track=track or road.getpixel((int(x*road.width),int(y*road.height)))>0
            if wet and track:return True
        return False
    return hit

def map_points(instance,north,east,zones):
    return [dict(mapID=z['id'],x=(z['west']-east)/(z['west']-z['east']),y=(z['north']-north)/(z['north']-z['south']))
            for z in zones if z.get('terrainMap')==instance and z['east']<=east<=z['west'] and z['south']<=north<=z['north']]

def placements(raw):
    cs={t:raw[a:b] for t,a,b in chunks(raw)};out=[]
    for tag,size,kind in [('MODF',64,'wmo'),('MDDF',36,'m2')]:
        blob=cs.get(tag,b'')
        if len(blob)%size:raise ValueError('Truncated '+tag)
        for at in range(0,len(blob),size):
            fid,uid=struct.unpack_from('<II',blob,at)
            q=dict(kind=kind,fdid=fid,uid=uid,pos=list(struct.unpack_from('<3f',blob,at+8)),rot=list(struct.unpack_from('<3f',blob,at+20)))
            if kind=='wmo':
                q.update(bounds=list(struct.unpack_from('<6f',blob,at+32)),flags=struct.unpack_from('<H',blob,at+56)[0],scale=struct.unpack_from('<H',blob,at+62)[0])
            else:q.update(scale=struct.unpack_from('<H',blob,at+32)[0],flags=struct.unpack_from('<H',blob,at+34)[0])
            direct=q['flags']&(8 if kind=='wmo' else 64)
            if not direct:
                indices=cs.get('MWID' if kind=='wmo' else 'MMID',b'');names=cs.get('MWMO' if kind=='wmo' else 'MMDX',b'')
                if fid*4+4<=len(indices):
                    offset=struct.unpack_from('<I',indices,fid*4)[0]
                    q['legacyName']=names[offset:].split(b'\0',1)[0].decode('utf8','replace')
                q['unresolvedNameIndex']=True
            out.append(q)
    return out

def asset_info(casc,kind,fid):
    try:
        raw=casc.read_fdid(fid);result=dict(sha256=hashlib.sha256(raw).hexdigest())
        if kind=='wmo':
            cs={t:raw[a:b] for t,a,b in chunks(raw)}
            result['name']=' '.join(cs.get('MOGN',b'').decode('utf8','replace').split('\0'))
            if 'MOHD' in cs:
                result['bounds']=list(struct.unpack_from('<6f',cs['MOHD'],36))
            result['groups']=list(struct.unpack('<'+'I'*(len(cs.get('GFID',b''))//4),cs.get('GFID',b'')))
            result['embeddedModels']=list(struct.unpack('<'+'I'*(len(cs.get('MODI',b''))//4),cs.get('MODI',b'')))
        else:
            at=raw.find(b'MD20')
            if at<0:raise ValueError('Missing MD20 model header')
            count,offset=struct.unpack_from('<II',raw,at+8)
            result['name']=raw[at+offset:at+offset+count].rstrip(b'\0').decode('utf8','replace')
            indices,indexOffset,vertices,vertexOffset=struct.unpack_from('<4I',raw,at+216)
            result['collisionTriangles']=indices//3
            if vertices:
                vs=list(struct.iter_unpack('<3f',raw[at+vertexOffset:at+vertexOffset+vertices*12]))
                result['bounds']=[min(v[k] for v in vs) for k in range(3)]+[max(v[k] for v in vs) for k in range(3)]
        return result
    except (ValueError,KeyError,FileNotFoundError,NotImplementedError,struct.error) as e:return dict(error=str(e),name='')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,default=ROOT.parent/'output/forever-datamine-70959')
    args=parser.parse_args();snapshot=args.snapshot.resolve()
    out=ROOT.parent/'output/bridges-and-crossings-70959'
    if out.resolve().is_relative_to(snapshot):raise ValueError('Audit output must be outside the read-only snapshot')
    out.mkdir(exist_ok=True)
    db=snapshot/'terrain-research/ashenvale/raw/dbfilesclient'
    maps=list(csv.DictReader((db/'map.csv').open(encoding='utf-8-sig')))
    zones=json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']
    casc=LocalCasc(snapshot);records={};map_report=[];errors=[];assets={}
    asset_path=out/'assets.json'
    if asset_path.exists():assets=json.loads(asset_path.read_text())
    for m in maps:
        mid=int(m['ID']);wdt=int(m['WdtFileDataID']);cache=out/f'map-{mid}.json'
        if cache.exists():data=json.loads(cache.read_text())
        else:
            data=dict(id=mid,name=m['MapName_lang'],instanceType=int(m['InstanceType']),wdt=wdt,placements=[],errors=[],tiles=0)
            try:
                raw=casc.read_fdid(wdt) if wdt else b''
                cs={t:raw[a:b] for t,a,b in chunks(raw)};data['wdtSha256']=hashlib.sha256(raw).hexdigest()
                seen={}
                for q in placements(raw):seen[(q['kind'],q['uid'])]=q
                maid=cs.get('MAID',b'')
                for tile in range(len(maid)//32):
                    ids=struct.unpack_from('<8I',maid,tile*32)
                    if not any(ids):continue
                    data['tiles']+=1
                    for fid in sorted(set(i for i in (ids[0],ids[1],ids[2]) if i)):
                        try:
                            for q in placements(casc.read_fdid(fid)):
                                key=(q['kind'],q['uid'])
                                if key in seen and any(seen[key][k]!=q[k] for k in ('fdid','pos','rot')):
                                    data['errors'].append(dict(fdid=fid,error='Conflicting placement identity',kind=q['kind'],uid=q['uid']))
                                else:seen[key]=q
                        except (ValueError,KeyError,FileNotFoundError,NotImplementedError,struct.error) as e:data['errors'].append(dict(fdid=fid,error=str(e)))
                data['placements']=list(seen.values())
                if not wdt:data['errors'].append(dict(error='No WDT FileDataID'))
            except (ValueError,KeyError,FileNotFoundError,NotImplementedError,struct.error) as e:data['errors'].append(dict(fdid=wdt,error=str(e)))
            cache.write_text(json.dumps(data,separators=(',',':')))
        for q in data['placements']:
            q=dict(q,map=mid);records[placement_key(mid,q['kind'],q['uid'])]=q
        entry={k:v for k,v in data.items() if k!='placements'}
        entry['terrainUIMaps']=[z['id']for z in zones if z.get('type')in(3,6)and z.get('terrainMap')==mid and (ROOT.parent/f"output/terrain-overlays-70959/{z['id']}.png").exists()]
        entry['groundAuditStatus']='terrain-supported'if entry['terrainUIMaps']else'no-UI-terrain-mask'
        if not entry['terrainUIMaps']and data['errors']:entry['groundAuditStatus']='source-unavailable-and-no-UI-terrain-mask'
        map_report.append(entry)
        print('Map',mid,data['name'],'placements',len(data['placements']),'errors',len(data['errors']),flush=True)
    wanted={(q['kind'],q['fdid']) for q in records.values() if not q.get('unresolvedNameIndex')}
    for i,(kind,fid) in enumerate(sorted(wanted)):
        key=f'{kind}:{fid}'
        if key not in assets:assets[key]=asset_info(casc,kind,fid)
        # Embedded models can contain a bridge even when their WMO's name does not.
        for embedded in assets[key].get('embeddedModels',[]):
            ek=f'm2:{embedded}'
            if ek not in assets:assets[ek]=asset_info(casc,'m2',embedded)
        if i%200==0:
            asset_path.write_text(json.dumps(assets,separators=(',',':')))
            print('Assets',i,'/',len(wanted),flush=True)
    asset_path.write_text(json.dumps(assets,separators=(',',':')))
    paths_file=out/'asset-paths.json'
    paths=json.loads(paths_file.read_text()) if paths_file.exists() else {}
    for key,asset in assets.items():asset['path']=paths.get(key.split(':')[1],'')
    floor_proofs={}
    zone_by_id={z['id']:z for z in zones}
    corridor_ids={}
    for proof_file in ['native-gate-corridors-70959.json','native-curved-corridors-70959.json','native-southfury-bridge-70959.json','native-bridge-batch-70959.json','native-bridge-expanded-70959.json','native-dun-algaz-70959.json']:
        proof_path=ROOT/'tools/data'/proof_file
        if not proof_path.exists():continue
        for proof in json.loads(proof_path.read_text()):
            if proof_file=='native-bridge-expanded-70959.json'and not(proof.get('isBridgeAsset')and proof.get('verificationRevision')==3):continue
            uid=proof.get('placement',proof.get('placementUID'));mid=proof['fromUiMap']
            key=proof.get('placementKey',placement_key(zone_by_id[mid]['terrainMap'],'wmo',uid))
            floor_proofs[key]=proof_file;corridor_ids.setdefault(key,[]).append(proof.get('corridorID',uid))
    batch_path=out/'bridge-family-validation.json'
    batch={r['key']:r for r in json.loads(batch_path.read_text())} if batch_path.exists() else {}
    expanded=out/'expanded-validation.json'
    if expanded.exists():batch.update({r['key']:r for r in json.loads(expanded.read_text())})
    reprobe=out/'native-bridge-expanded-70959-reprobe.json'
    if not reprobe.exists():reprobe=out/'expanded-reprobe.json'
    if reprobe.exists():
        for r in json.loads(reprobe.read_text()):
            if r['status']=='rejected':batch[r['key']]=dict(status='unresolved',reason=r['reason'],stage='independent-floor-liquid-reprobe')
    candidates=[];missing=collections.Counter();overlap=overlap_detector(zones)
    for key,q in sorted(records.items()):
        asset=assets.get(f"{q['kind']}:{q['fdid']}",dict(error='Legacy name index needs lookup',name=q.get('legacyName','')))
        reasons=candidate_reasons(asset)
        if not reasons and overlap(q,asset):reasons.append('road-water-overlap')
        embedded=[f for f in asset.get('embeddedModels',[]) if candidate_reasons(assets.get(f'm2:{f}',{}))]
        if embedded:reasons.append('embedded-model')
        if asset.get('error'):missing[f"{q['kind']}:{q['fdid']}"]+=1
        if reasons:
            north,east=ORIGIN-q['pos'][2],ORIGIN-q['pos'][0]
            candidates.append(dict(key=key,**q,assetName=asset.get('name',''),assetPath=asset.get('path',''),reasons=reasons,embeddedCandidates=embedded,
                maps=map_points(q['map'],north,east,zones),worldNorth=north,worldEast=east,
                sourceStatus='certified-corridor' if key in floor_proofs else 'unresolved',proof=floor_proofs.get(key),corridorIDs=corridor_ids.get(key,[]),
                validation=batch.get(key),liveStatus='not-tested'))
    inventory=json.loads((ROOT.parent/'output/zone-crossings-70959/inventory.json').read_text())
    audit=json.loads((ROOT.parent/'output/zone-crossings-70959/coverage-audit.json').read_text())
    pairs=collections.defaultdict(list)
    for e in inventory['crossings']:pairs[tuple(sorted((e['a']['mapID'],e['b']['mapID'])))].append(e['id'])
    approaches=json.loads((ROOT/'tools/data/crossing-approaches-manifest.json').read_text())
    verify_inventory((ROOT.parent/'output/zone-crossings-70959/inventory.json').read_bytes(),approaches)
    approach_by_id={r['id']:r['sides']for r in approaches['links']}
    reviews=json.loads((ROOT/'tools/data/crossing-handoff-review.json').read_text())
    boundaries=[]
    for p in audit['pairs']:
        key=tuple(sorted((p['a'],p['b'])))
        links=pairs.get(key,[])
        boundaries.append(dict(**p,links=links,status='has-bundled-link' if links else 'unresolved-no-certified-exit',
            approachResults={str(id):approach_by_id[id]for id in links},
            withheldHandoffs=[r for r in reviews['handoffs']if (r['a'],r['b'])==key],liveStatus='not-tested'))
    non_walking,transport_exclusions=non_walking_inventory()
    result=dict(version=1,build=70959,targetClientBuild=71091,sourceBuildMismatch=True,maps=map_report,
        placements=len(records),assets=len(assets),candidates=candidates,unreadableAssets=dict(sorted(missing.items())),
        assetSources={k:v.get('sha256') for k,v in sorted(assets.items())},
        boundaries=boundaries,existingCrossings=inventory['crossings'],approachCounts=approaches['counts'],
        nonWalkingCrossings=non_walking,transportExclusions=transport_exclusions,
        limits=['Live verification is pending on reported client build 71091. The source snapshot is build 70959.',
                'Geometric/name candidates are a discovery superset, not certified bridges.',
                'Native ownership/ground approaches cover 55 UI terrain maps. All 73 native maps were scanned for placements; instances without UI terrain masks cannot receive ground permissions.',
                'Active embedded-model transforms and selected bridge groups were tested. Unsupported component contacts and missing floor coverage remain explicit per candidate.',
                'Missing or legacy assets are counted, never classified as safe.'])
    path=ROOT/'tools/data/bridges-and-crossings-manifest.json';path.write_text(json.dumps(result,indent=2)+'\n')
    text=['# Bridge and zone crossing audit','', '**Status: available-source audit complete; unresolved source coverage and live acceptance remain explicit. Discovery is not floor certification.**','',
          f"Snapshot build 70959. Reported live client build {result['targetClientBuild']}. Native maps: {len(map_report)}. Placements: {len(records)}. Candidate placements: {len(candidates)}.",
          '', '## Limits','']+['- '+s for s in result['limits']]
    text+=['','## Native map coverage','','| Map | Tiles | Errors | UI terrain maps | Ground audit |','| --- | ---: | ---: | --- | --- |']
    text += [f"| {m['id']} {m['name']} | {m['tiles']} | {len(m['errors'])} | {', '.join(map(str,m['terrainUIMaps'])) or 'none'} | {m['groundAuditStatus']} |" for m in map_report]
    text+=['','## Bridge candidates','','Full identities, coordinates, placement transforms, source hashes and individual validation results are in `tools/data/bridges-and-crossings-manifest.json`. A certified corridor covers its proven path, not an entire compound asset. All live acceptance remains pending.','','| Native map | Candidates | Certified corridors |','| --- | ---: | ---: |']
    for mid in sorted({p['map'] for p in candidates}):
        rows=[p for p in candidates if p['map']==mid]
        text.append(f"| {mid} | {len(rows)} | {sum(p['sourceStatus']=='certified-corridor' for p in rows)} |")
    text+=['','## Zone boundary accounting','',f"{len(boundaries)} audited ownership pairs; {sum(bool(p['links']) for p in boundaries)} have bundled links. A link's presence is not proof that every passage on that border has been checked.",'',
        'Approaches: '+', '.join(f"{v} {k}"for k,v in approaches['counts'].items())+'.',
        f"{len(reviews['handoffs'])} exact ground handoffs were withheld after the approach audit. Nearby replacement candidates were re-evaluated before spacing/pair selection. Their evidence remains in `tools/data/crossing-handoff-review.json`; no whole zone pair is banned.",
        'See `crossing-approaches-audit.md` and `testing-crossing-acceptance.md` for approach and live-test details.','']
    text+=['## Known transport and portal crossings','',
        'Each directed native record is accounted for separately. They retain the existing transport/portal mechanisms; none grants ordinary walking permission. All live acceptance is pending. Source hashes and full endpoints remain in the inventory.','',
        '| ID | Kind | Name | Source |','| --- | --- | --- | --- |']
    text += [f"| {r['id']} | {r['kind']} | {r['name']} | {r['source']} |"for r in non_walking]
    (ROOT/'docs/bridges-and-crossings-audit.md').write_text('\n'.join(text)+'\n',encoding='utf8')
    print('Inventory:',len(candidates),'candidates;',len(missing),'unreadable assets;',len(boundaries),'boundary pairs',flush=True)

if __name__=='__main__':main()
