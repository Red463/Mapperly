"""Audit pending placed bridges using full rotations and WMO/M2 collision floors.

Restartable. Successful proofs are separate from the first certified batch.
Discovery candidates never become permissions without floor and dry-bank proof.
"""
from pathlib import Path
import argparse,csv,hashlib,json,math,time
from bridge_geometry import Reader,placed,floor_path,placement_error
from build_southfury_bridge import runtime
from build_bridge_batch import dry_point
from build_structure_corridors import validate_curved
ROOT=Path(__file__).resolve().parents[1]

def corridor_id(key):return 2**48+int(hashlib.sha256(key.encode()).hexdigest()[:12],16)

def atomic_json(path,value,compact=False):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,separators=(',',':'))+'\n'if compact else json.dumps(value,indent=2)+'\n',encoding='utf8')
    # Windows readers may briefly hold a file without FILE_SHARE_DELETE.
    for attempt in range(40):
        try:temporary.replace(path);return
        except PermissionError:
            if attempt==39:raise
            time.sleep(.05)

def extract(reader,p,sampler,zones,owner,lua,part=None):
    mesh,asset,slack=reader.mesh(p,sampler,part)
    p=dict(p,proofTransformError=placement_error(asset['vertices'],p),proofSource=asset.get('source','native-model-floor'if p['kind']=='m2'else 'native-wmo-floor'),proofModel=asset.get('model',p['fdid']if p['kind']=='m2'else 0),selectedPart=part)
    vs=asset['vertices'];bounds=[min(v[k]for v in vs)for k in range(3)]+[max(v[k]for v in vs)for k in range(3)]
    axis=0 if bounds[3]-bounds[0]>bounds[4]-bounds[1]else 1
    local_center=[(bounds[k]+bounds[k+3])/2 for k in range(3)]
    # Use the horizontal projection of the native longitudinal axis. Floor
    # height is raycast in world space, including pitch/roll and model scale.
    lo=list(local_center);hi=list(local_center);lo[axis]=bounds[axis];hi[axis]=bounds[axis+3]
    a,b=asset.get('axisEnds',(placed(lo,p),placed(hi,p)));length=math.dist(a[:2],b[:2])
    if not 4<length<300:raise ValueError('Compound/large or non-bridge span needs selected geometry')
    dn,de=(b[0]-a[0])/length,(b[1]-a[1])/length
    def mapped(n,e,mid):
        z=zones[mid];return dict(mapID=mid,x=(z['west']-e)/(z['west']-z['east']),y=(z['north']-n)/(z['north']-z['south']))
    if p['key']=='0:wmo:67711058' and p['fdid']==7543871:
        return farholde_proof(reader,p,mesh,sampler,mapped,owner,slack,lua)
    def bank_contact(t,offset):
        north,east=a[0]+dn*t-de*offset,a[1]+de*t+dn*offset
        if not mesh.floor(north,east):return
        ground=reader.terrain(sampler,north,east);mid=owner(ground['area'])
        hit=mesh.floor(north,east,near=ground['height'])
        if not mid or not ground['permitted'] or not hit or hit[2]<2.2 or abs(hit[0]-ground['height'])>.3:return
        q=mapped(north,east,mid)
        if dry_point(lua,q):return t,[north,east,hit[0]],ground,q
    last_error='No independently dry contacts on opposite ends';contact_pairs=[]
    for offset in (0,-1,1,-2,2):
        def probe(t,lateral=0,near=None):
            n,e=a[0]+dn*t-de*(offset+lateral),a[1]+de*t+dn*(offset+lateral)
            hit=mesh.floor(n,e,near=near)
            return ([n,e,hit[0]],hit) if hit else (None,None)
        contacts=[]
        for i in range(math.ceil(length/.15)+1):
            contact=bank_contact(min(length,i*.15),offset)
            if contact:contacts.append(contact)
        first=[c for c in contacts if c[0]<length*.3];last=[c for c in contacts if c[0]>length*.7]
        if not first or not last:continue
        start,end=max(first,key=lambda c:c[0]),min(last,key=lambda c:c[0]);contact_pairs.append((start,end))
        count=math.ceil((end[0]-start[0])/.25);points=[];samples=[];used=set()
        failed=False
        for i in range(count+1):
            t=start[0]+(end[0]-start[0])*i/count;point,hit=probe(t,near=points[-1][2]if points else start[1][2])
            if not hit or hit[2]<2.2:
                failed=True;last_error='Centerline floor/clearance gap';break
            points.append(point);samples.append(dict(point=point,segment=min(i,count-1),headroom=hit[2]));used.add(hit[1])
        if failed:continue
        if abs(points[0][2]-start[2]['height'])>.3 or abs(points[-1][2]-end[2]['height'])>.3 or max(abs(x[2]-y[2])for x,y in zip(points,points[1:]))>.3:
            last_error='Unsupported vertical step';continue
        gap=max(mesh.gap(x,y)for x,y in zip(points,points[1:]))
        if gap>.03:last_error='Native floor interval gap';continue
        width=None
        for radius in (2.5,1.5,.75,.5):
            deltas=[];width_used=set();failed=False;across=round(2*radius/.25)
            for i,point in enumerate(points):
                t=start[0]+(end[0]-start[0])*i/count
                for k in range(across+1):
                    q,h=probe(t,-radius+k*.25,near=point[2])
                    if not h or h[2]<2.2 or abs(q[2]-point[2])>.3:
                        failed=True;break
                    deltas.append(q[2]-point[2]);width_used.add(h[1])
                if failed:break
            if not failed:
                width=dict(radiusYards=radius,sampleCount=len(deltas),lateralStepYards=.25,longitudinalStepYards=(end[0]-start[0])/count,minimumHeightDelta=min(deltas),maximumHeightDelta=max(deltas));used.update(width_used);break
        if not width:last_error='No supported central strip at least one yard wide';continue
        return proof_row(reader,p,mesh,points,samples,used,start,end,width,gap,slack,lua)
    for start,end in contact_pairs[:1]:
        path=floor_path(mesh,start[1],end[1])
        if path:
            try:return curved_proof(reader,p,mesh,path,start,end,slack,lua)
            except ValueError as error:last_error=str(error)
    if p['key']=='0:m2:44103' and p['fdid']==189411:
        # The two chasm banks contact different sides of the deck. Keep the
        # lane parallel to its axis through each end plane so its full width
        # has collision support, then cross between the rails on the deck.
        path=[];banks=[];strips=[]
        for t,offset,inside in ((0,-3,.25),(length,5,-.25)):
            strip=[]
            for lateral in (-.5,-.25,0,.25,.5):
                contact=bank_contact(t,offset+lateral)
                if not contact:raise ValueError('Missing dry contact across chasm bridge landing')
                _,point,ground,q=contact
                strip.append(dict(offsetYards=lateral,world=point,mapPoint=q,**ground,terrainDelta=point[2]-ground['height']))
                if lateral==0:banks.append(contact)
            strips.append(strip)
            landing=banks[-1][1]
            north,east=landing[0]+dn*inside,landing[1]+de*inside
            floor=mesh.floor(north,east,near=landing[2])
            if not floor:raise ValueError('Missing chasm bridge entry floor')
            entry=[north,east,floor[0]]
            path.extend((landing,entry) if t==0 else (entry,landing))
        # Inventory dispositions are outputs of this proof and can change on
        # the next audit. Only stable placement and asset facts belong here.
        placement={k:v for k,v in p.items() if k not in ('proof','sourceStatus','corridorIDs','liveStatus','validation')}
        row=curved_proof(reader,placement,mesh,path,*banks,slack,lua)
        for landing,strip in zip(row['landings'],strips):landing['stripContacts']=strip
        row['method']='bank-specific native floor trace with full-width dry contacts and exact triangle interval checks'
        return row
    raise ValueError(last_error)

def farholde_proof(reader,p,mesh,sampler,mapped,owner,slack,lua):
    # The centre of this damaged deck is split. Sample the raised strip on
    # the keep side of the break, then rejoin the middle of the intact span.
    knots=[(-63,11.6),(-12,11.6),(4,0),(62,0)]
    points=[]; samples=[]; used=set(); banks=[]; deltas=[]; kerbs=[]; gap=0
    for j,(a,b) in enumerate(zip(knots,knots[1:])):
        span=math.dist(a,b); count=math.ceil(span/.2)
        ux,uy=(b[0]-a[0])/span,(b[1]-a[1])/span
        for i in range(count+int(j==len(knots)-2)):
            x,y=a[0]+i/count*(b[0]-a[0]),a[1]+i/count*(b[1]-a[1])
            n,e,_=placed([x,y,0],p)
            ground=reader.terrain(sampler,n,e)
            near=points[-1][2] if points else ground['height']
            hits=[h for h in mesh.floors(n,e) if h[2]>=2.2]
            if not hits:raise ValueError('Farholde deck floor or headroom missing')
            z,face,clearance=min(hits,key=lambda h:abs(h[0]-near))
            point=[n,e,z]; used.add(face)
            if points:
                gap=max(gap,mesh.gap(points[-1],point))
                if abs(z-near)>.3:kerbs.append(len(points))
            if ground['liquid'] and (ground['liquidHigh'] is None or z<ground['liquidHigh']+.1):
                raise ValueError('Farholde deck below water')
            for offset in (-.5,-.25,0,.25,.5):
                sn,se,_=placed([x-uy*offset,y+ux*offset,0],p)
                hit=mesh.floor(sn,se,near=z)
                if not hit or hit[2]<2.2 or abs(hit[0]-z)>.3:raise ValueError('Farholde deck width unsupported')
                used.add(hit[1]); deltas.append(hit[0]-z)
            if not points or (j==len(knots)-2 and i==count):
                mid=owner(ground['area'])
                if mid!=2548:raise ValueError('Farholde landing in unexpected zone')
                q=mapped(n,e,mid)
                if not ground['permitted'] or not dry_point(lua,q):raise ValueError('Farholde landing inaccessible')
                banks.append((0,point,ground,q))
            samples.append(dict(point=point,segment=len(points),headroom=clearance));points.append(point)
    samples[-1]['segment']-=1
    width=dict(radiusYards=.5,sampleCount=len(deltas),lateralStepYards=.25,longitudinalStepYards=.2,
               minimumHeightDelta=min(deltas),maximumHeightDelta=max(deltas))
    p={k:v for k,v in p.items() if k not in ('proof','sourceStatus','corridorIDs','liveStatus','validation')}
    return proof_row(reader,p,mesh,points,samples,used,*banks,width,gap,slack,lua,kerbs)

def proof_row(reader,p,mesh,points,samples,used,start,end,width,gap,slack,lua,kerbs=None):
    faces=[dict(v=mesh.faces[i]['v'],sourceGroup=mesh.faces[i]['group'],sourceTriangle=mesh.faces[i]['triangle'],sourceFlags=mesh.faces[i]['flags'])for i in sorted(used)]
    # No new corridor is needed for an already dry, permitted ground line.
    whole=dict(mapID=start[3]['mapID'],x=end[3]['x'],y=end[3]['y']) if start[3]['mapID']==end[3]['mapID']else None
    existing=whole is not None and lua.eval('function(a,b) return A.Terrain.Segment(a,b,{allowSwimming=false}) end')(lua.table_from(start[3]),lua.table_from(whole)) is True
    row=dict(name=p.get('assetName','Bridge').strip()+' '+str(p['uid']),corridorID=corridor_id(p['key']+(':'+p['selectedPart']if p.get('selectedPart')else '')),placement=p['uid'],placementKey=p['key'],
        source=p['proofSource'],wmo=p['fdid']if p['kind']=='wmo'else 0,model=p['proofModel'],
        fromUiMap=start[3]['mapID'],toUiMap=end[3]['mapID'],build=70959,worldCenterline=points,samples=samples,faces=faces,
        landings=[dict(**c[2],mapPoint=c[3],world=point,terrainDelta=point[2]-c[2]['height'])for c,point in zip((start,end),(points[0],points[-1]))],
        transformError=p['proofTransformError'],portalGap=gap,maximumStep=max(abs(x[2]-y[2])for x,y in zip(points,points[1:])),minimumHeadroom=min(s['headroom']for s in samples),widthProof=width,
        nativePlacement=p,nativeBoundsSlack=slack,provenance=dict(fdidSha256=dict(reader.used)),existingGroundLine=existing)
    row['isBridgeAsset']=bool(p.get('selectedPart'))or any(w in p.get('assetPath','').lower()for w in('bridge','viaduct','causeway'))
    if kerbs is not None:row['kerbSteps']=kerbs
    validate_curved(row)
    return row

def curved_proof(reader,p,mesh,path,start,end,slack,lua):
    points=[];samples=[];used=set()
    for a,b in zip(path,path[1:]):
        length=math.dist(a[:2],b[:2])
        if length<1e-8:continue
        count=math.ceil(length/.24)
        for k in range(count):
            t=k/count;n,e=a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])
            h=mesh.floor(n,e,near=a[2]+t*(b[2]-a[2]))
            if not h or h[2]<2.2:raise ValueError('Winding floor lacks clearance')
            points.append([n,e,h[0]]);used.add(h[1]);samples.append(dict(point=points[-1],headroom=h[2]))
    h=mesh.floor(*end[1][:2],near=end[1][2]);points.append(end[1]);used.add(h[1]);samples.append(dict(point=end[1],headroom=h[2]))
    for i,s in enumerate(samples):s['segment']=min(i,len(points)-2)
    if max(abs(a[2]-b[2])for a,b in zip(points,points[1:]))>.3:raise ValueError('Winding floor has excessive step')
    gap=max(mesh.gap(a,b)for a,b in zip(points,points[1:]))
    if gap>.03:raise ValueError('Winding floor has native interval gap')
    deltas=[]
    for i,q in enumerate(points):
        a,b=points[max(0,i-1)],points[min(len(points)-1,i+1)];length=math.dist(a[:2],b[:2])
        if length<1e-8:raise ValueError('Degenerate winding corner')
        dn,de=(b[0]-a[0])/length,(b[1]-a[1])/length
        for k in range(5):
            offset=-.5+k*.25;h=mesh.floor(q[0]-de*offset,q[1]+dn*offset,near=q[2])
            if not h or h[2]<2.2 or abs(h[0]-q[2])>.3:raise ValueError('Winding floor lacks one-yard central strip')
            deltas.append(h[0]-q[2]);used.add(h[1])
    width=dict(radiusYards=.5,sampleCount=len(deltas),lateralStepYards=.25,longitudinalStepYards=max(math.dist(a[:2],b[:2])for a,b in zip(points,points[1:])),minimumHeightDelta=min(deltas),maximumHeightDelta=max(deltas))
    row=proof_row(reader,p,mesh,points,samples,used,start,end,width,gap,slack,lua);row['method']='layered native floor search; exact triangle interval checks'
    return row

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',nargs='*');parser.add_argument('--resume',action='store_true');parser.add_argument('--named-only',action='store_true')
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--refine',action='store_true',help='Recheck proofs and cases affected by layered/compound geometry; retain unchanged coverage/asset rejections')
    args=parser.parse_args();out=ROOT.parent/'output/bridges-and-crossings-70959'
    snapshot=ROOT.parent/'output/forever-datamine-70959';db=snapshot/'terrain-research/ashenvale/raw/dbfilesclient'
    manifest=json.loads((ROOT/'tools/data/bridges-and-crossings-manifest.json').read_text())
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']if z.get('type')in(3,6) and 'wdt'in z and z['id']!=2665}
    wdts={z['terrainMap']:z['wdt']for z in zones.values()}
    areas={int(r['ID']):r for r in csv.DictReader((db/'areatable.csv').open(encoding='utf-8-sig'))}
    owners={int(r['AreaID']):int(r['UiMapID'])for r in csv.DictReader((db/'uimapassignment.csv').open(encoding='utf-8-sig'))if int(r['UiMapID'])in zones and int(r['AreaID'])}
    def owner(area):
        seen=set()
        while area and area not in seen:
            if area in owners:return owners[area]
            seen.add(area);area=int(areas.get(area,{}).get('ParentAreaID',0))
    lua=runtime()
    for name in ['Data/Water.lua','Water.lua']:lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/name).read_text())
    provenance={str(p.relative_to(ROOT))if p.is_relative_to(ROOT)else str(p.relative_to(snapshot)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [db/'areatable.csv',db/'uimapassignment.csv']+[ROOT/n for n in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/Water.lua','Terrain.lua','Water.lua']]}
    reader=Reader(snapshot);report_file=out/'expanded-validation.json';proof_file=ROOT/'tools/data/native-bridge-expanded-70959.json'
    report=json.loads(report_file.read_text())if report_file.exists()else []
    proofs=json.loads(proof_file.read_text())if proof_file.exists()else []
    done={r['key']for r in report}if args.resume else set()
    selected=[p for p in manifest['candidates']if not args.only or p['key']in args.only]
    if args.named_only:selected=[p for p in selected if any(r in p['reasons']for r in('name','asset-path','embedded-model'))]
    if args.refine:
        prior={r['key']:r for r in report}
        changed={'No independently dry contacts on opposite ends','Unsupported vertical step','Centerline floor/clearance gap','No supported central strip at least one yard wide'}
        selected=[p for p in selected if prior.get(p['key'],{}).get('status')=='floor-validated' or prior.get(p['key'],{}).get('reason')in changed or 'name'in p['reasons']or 'embedded-model'in p['reasons']]
    for i,p in enumerate(selected):
        key=p['key']
        recheck=args.only and p.get('proof')==proof_file.name
        if key in done or p.get('sourceStatus')=='certified-corridor' and not recheck:continue
        row=dict(key=key,status='unresolved',revision=2)
        # A failed re-extraction must revoke its earlier provisional proof.
        insertion=next((index for index,proof in enumerate(proofs) if proof['placementKey']==key),len(proofs))
        proofs=[r for r in proofs if r['placementKey']!=key]
        if p['map']not in wdts:row['reason']='No shipped terrain/map routing coverage for this native map'
        else:
            try:
                reader.used={};sampler=reader.sampler(p['map'],wdts[p['map']]);found=[]
                try:
                    found=[extract(reader,p,sampler,zones,owner,lua)]
                    if not found[0]['isBridgeAsset']:
                        parts=[]
                        for part in reader.parts(p):
                            try:parts.append(extract(reader,p,sampler,zones,owner,lua,part))
                            except ValueError:pass
                        if parts:found=parts
                except ValueError as error:
                    first_error=error
                    row['partFailures']={}
                    for part in reader.parts(p):
                        try:found.append(extract(reader,p,sampler,zones,owner,lua,part))
                        except ValueError as part_error:row['partFailures'][part]=str(part_error)
                    if not found:raise first_error
                for proof in found:proof['provenance']['admissionSourcesSha256']=provenance
                proof=found[0]
                row.update(status='floor-validated',corridor=proof['corridorID'],corridors=[r['corridorID']for r in found],maps=[proof['fromUiMap'],proof['toUiMap']],radius=proof['widthProof']['radiusYards'],existingGroundLine=all(r['existingGroundLine']for r in found))
                # The crossing builder assigns link ordinals in proof order.
                proofs[insertion:insertion]=found
            except (ValueError,KeyError,FileNotFoundError,NotImplementedError,StopIteration,struct_error())as e:row['reason']=str(e)
        report=[r for r in report if r['key']!=key]+[row]
        if not args.dry_run:
            atomic_json(proof_file,proofs,compact=True)
            atomic_json(report_file,report)
        print(i+1,'/',len(selected),row,flush=True)

def struct_error():
    import struct
    return struct.error

if __name__=='__main__':main()
