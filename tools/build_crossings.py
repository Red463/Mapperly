"""Build conservative outdoor zone crossings from native area ownership and roads."""
from pathlib import Path
import csv,json,math,struct,sys,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'));sys.path.insert(0,str(ROOT/'tools'))
from build_roads import LocalCasc,chunks,TILE,CELL,ORIGIN
from PIL import Image
from lupa.lua51 import LuaRuntime

def reviewed_handoffs(selected,reviews):
    """Quarantine exact unsupported landings, never an entire zone pair."""
    blocked={(r['a'],r['b'],*(round(v,6)for v in r['worldA']),*(round(v,6)for v in r['worldB']))
             for r in reviews if r['status']=='withheld-unproven-approach'}
    return [r for r in selected if (r[0],r[1],*(round(v,6)for v in r[2]),*(round(v,6)for v in r[3]))not in blocked]

def select_road_crossings(candidates,reviews):
    selected=[]
    for a,b,p,q in sorted(reviewed_handoffs(candidates,reviews)):
        if any(a==old[0] and b==old[1] and math.dist(p,old[2])<100 for old in selected):continue
        selected.append((a,b,p,q))
    return selected

def select_dry_crossings(samples,recorded,score,limit=3):
    """Only receives independently dry/terrain-validated native boundaries."""
    result=[]
    for pair,points in sorted(samples.items()):
        if pair in recorded:continue
        chosen=[]
        for a,b in sorted(points,key=lambda p:(score(pair[0],p[0])+score(pair[1],p[1]),p)):
            if any(math.dist(a,old)<100 for old in chosen):continue
            chosen.append(a);result.append((*pair,a,b))
            if len(chosen)>=limit:break
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-only',action='store_true')
    args=parser.parse_args()
    source=ROOT.parent/'output/forever-datamine-70959'
    out=ROOT.parent/'output/zone-crossings-70959';out.mkdir(exist_ok=True)
    cache=out/'area-cache';cache.mkdir(exist_ok=True)
    db=source/'terrain-research/ashenvale/raw/dbfilesclient'
    def table(name):return list(csv.DictReader((db/(name+'.csv')).open(encoding='utf-8-sig')))
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones'] if z['type'] in (3,6) and 'wdt' in z}
    aliases={};seen={}
    for id,z in zones.items():
        key=tuple(z[k] for k in ['terrainMap','north','south','west','east'])
        if key in seen:aliases[id]=seen[key]
        else:seen[key]=id
    # Native root terrain does not certify underground capital entrances.
    excluded={1455,1458};eligible={id:z for id,z in zones.items() if id not in aliases and id not in excluded}
    areas={int(r['ID']):r for r in table('areatable')};owners={}
    for r in table('uimapassignment'):
        id=int(r['UiMapID']);area=int(r['AreaID'])
        if id in eligible and area:owners[area]=id
    def owner(area):
        visited=set()
        while area and area not in visited:
            if area in owners:return owners[area]
            visited.add(area);area=int(areas.get(area,{}).get('ParentAreaID',0))
    c=LocalCasc(source);wdts={};tiles={};grid={};unassigned={}
    for z in eligible.values():
        if z['wdt'] not in wdts:
            b=c.read_fdid(z['wdt']);wdts[z['wdt']]=next(b[a:e] for tag,a,e in chunks(b) if tag=='MAID')
        maid=wdts[z['wdt']]
        for y in range(math.floor((ORIGIN-z['north'])/TILE),math.floor((ORIGIN-z['south'])/TILE)+1):
            for x in range(math.floor((ORIGIN-z['west'])/TILE),math.floor((ORIGIN-z['east'])/TILE)+1):
                key=(z['terrainMap'],x,y)
                if key in tiles:continue
                fdid=struct.unpack_from('<I',maid,(y*64+x)*32)[0];tiles[key]=fdid
                if not fdid:continue
                try:
                    path=cache/f'{fdid}.json'
                    if path.exists():values=json.loads(path.read_text())
                    else:
                        b=c.read_fdid(fdid);values=[]
                        for tag,a,e in chunks(b):
                            if tag=='MCNK':
                                cx,cy=struct.unpack_from('<2I',b,a+4);area=struct.unpack_from('<I',b,a+52)[0]
                                values.append([cx,cy,area])
                        path.write_text(json.dumps(values))
                    for cx,cy,area in values:
                        id=owner(area)
                        if id and eligible[id]['terrainMap']==z['terrainMap']:grid[(z['terrainMap'],x*16+cx,y*16+cy)]=id
                        elif area:unassigned[(z['terrainMap'],x*16+cx,y*16+cy)]=area
                except (ValueError,FileNotFoundError,NotImplementedError):pass
    print('Native area ownership:',len(grid),'chunks',len(tiles),'tiles',flush=True)
    roadroot=ROOT.parent/'output/road-overlays-70959'
    roads={id:Image.open(roadroot/f'{id}-mask.png').convert('L') for id in eligible}
    terrainroot=ROOT.parent/'output/terrain-overlays-70959'
    terrain={id:Image.open(terrainroot/f'{id}.png').convert('L') for id in eligible}
    lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={}')
    for name in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Terrain.lua','WalkingRegions.lua']:lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/name).read_text())
    safe=lua.eval('function(id,ax,ay,bx,by) return A.Terrain.Segment({mapID=id,x=ax,y=ay},{mapID=id,x=bx,y=by}) end')
    region=lua.eval('function(id,x,y) return A.WalkingRegions.Get({mapID=id,x=x,y=y}) end')
    def local(id,wx,wy):
        z=zones[id];return (z['west']-wx)/(z['west']-z['east']),(z['north']-wy)/(z['north']-z['south'])
    def road(id,wx,wy):
        x,y=local(id,wx,wy);im=roads[id]
        return 0<=x<1 and 0<=y<1 and im.getpixel((int(x*im.width),int(y*im.height)))>0
    def bridge(id,a,b):
        ax,ay=local(id,*a);bx,by=local(id,*b)
        return safe(id,ax,ay,bx,by)
    def dry(id,p):
        x,y=local(id,*p);im=terrain[id]
        return 0<=x<1 and 0<=y<1 and im.getpixel((int(x*im.width),int(y*im.height)))==255
    distances={}
    def road_distance(id,p):
        if id not in distances:
            im=roads[id];small=im.resize((math.ceil(im.width/8),math.ceil(im.height/8)),Image.Resampling.BOX)
            w,h=small.size;values=[0 if v else 1000000 for v in small.tobytes()]
            for y in range(h):
                for x in range(w):
                    at=y*w+x
                    if x:values[at]=min(values[at],values[at-1]+1)
                    if y:values[at]=min(values[at],values[at-w]+1)
            for y in range(h-1,-1,-1):
                for x in range(w-1,-1,-1):
                    at=y*w+x
                    if x+1<w:values[at]=min(values[at],values[at+1]+1)
                    if y+1<h:values[at]=min(values[at],values[at+w]+1)
            distances[id]=(w,h,values)
        w,h,values=distances[id];x,y=local(id,*p)
        return values[min(h-1,max(0,int(y*h)))*w+min(w-1,max(0,int(x*w)))]+(0 if region(id,x,y)==1 else 10000000)
    candidates=[];audit={};plain={}
    for (instance,x,y),first in sorted(grid.items()):
        for dx,dy in [(1,0),(0,1)]:
            second=grid.get((instance,x+dx,y+dy))
            if not second or first==second:continue
            if {first,second}=={1413,1441}:continue # Great Lift needs a transport leg.
            pair=tuple(sorted((first,second)))
            record=audit.setdefault(pair,dict(a=pair[0],b=pair[1],boundaryChunks=0,drySafeSamples=0,roadSamples=0))
            record['boundaryChunks']+=1
            for offset in range(8):
                gx=x*8+(7 if dx else offset);gy=y*8+(7 if dy else offset)
                a=(ORIGIN-(gx+.5)*CELL,ORIGIN-(gy+.5)*CELL)
                b=(a[0]-dx*CELL,a[1]-dy*CELL)
                if dry(first,a) and dry(second,b) and bridge(first,a,b) and bridge(second,a,b):
                    record['drySafeSamples']+=1
                    aa,bb=(a,b) if first<second else (b,a)
                    samples=plain.setdefault(pair,[])
                    samples.append((aa,bb))
                # Geometry-only bridges/short texture gaps may separate the
                # two road approaches. Keep both endpoints on their own area
                # and validate the entire short connector in both masks.
                def approach(id,p,sign):
                    for step in range(16):
                        q=(p[0]+sign*dx*CELL*step,p[1]+sign*dy*CELL*step)
                        qx,qy=math.floor((ORIGIN-q[0])/(TILE/16)),math.floor((ORIGIN-q[1])/(TILE/16))
                        if grid.get((instance,qx,qy))==id and road(id,*q):return q
                startA,startB=a,b
                a,b=approach(first,a,1),approach(second,b,-1)
                if a and not b:b=startB
                elif b and not a:a=startA
                if not a or not b or math.dist(a,b)>120:continue
                if not bridge(first,a,b) or not bridge(second,a,b):continue
                record['roadSamples']+=1
                if first>second:firstID,secondID,aa,bb=second,first,b,a
                else:firstID,secondID,aa,bb=first,second,a,b
                candidates.append((firstID,secondID,aa,bb))
    review_file=ROOT/'tools/data/crossing-handoff-review.json'
    reviews=json.loads(review_file.read_text())if review_file.exists()else {}
    if reviews and reviews.get('build')!=70959:raise ValueError('Handoff review build mismatch')
    review_rows=reviews.get('handoffs',[])
    selected=select_road_crossings(candidates,review_rows)
    plain={pair:[(r[2],r[3])for r in reviewed_handoffs([(*pair,a,b)for a,b in points],review_rows)]for pair,points in plain.items()}
    recorded={(a,b) for a,b,_,_ in selected}
    additions=select_dry_crossings(plain,recorded,road_distance)
    for pair,record in audit.items():
        record['names']=[zones[pair[0]]['name'],zones[pair[1]]['name']]
        record['roadRecorded']=pair in recorded
        record['recorded']=pair in recorded or any((a,b)==pair for a,b,_,_ in additions)
        record['dryCandidates']=[dict(a=list(a),b=list(b)) for aa,bb,a,b in additions if (aa,bb)==pair]
    unknown=[];visited=set()
    for start,area in unassigned.items():
        if start in visited:continue
        queue=[start];visited.add(start);adjacent=set();areaids=set()
        for instance,x,y in queue:
            areaids.add(unassigned[(instance,x,y)])
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                key=(instance,x+dx,y+dy)
                if key in grid:adjacent.add(grid[key])
                elif key in unassigned and key not in visited:visited.add(key);queue.append(key)
        if len(adjacent)>1:unknown.append(dict(chunks=len(queue),areas=[dict(id=id,name=areas.get(id,{}).get('AreaName_lang','Unknown')) for id in sorted(areaids)],neighbors=[dict(id=id,name=zones[id]['name']) for id in sorted(adjacent)]))
    (out/'coverage-audit.json').write_text(json.dumps(dict(pairs=list(audit.values()),unassignedRegions=unknown),indent=2))
    if args.audit_only:
        for record in audit.values():
            if not record['recorded']:print('MISSING',record['names'],'safe dry samples',record['drySafeSamples'],flush=True)
        print('UNASSIGNED REGIONS',len(unknown));return
    selected.extend(additions)
    maps={str(id):dict(name=z['name'],west=z['west'],north=z['north'],width=z['west']-z['east'],height=z['north']-z['south'],instance=z['terrainMap']) for id,z in zones.items()}
    edges=[]
    for i,(a,b,p,q) in enumerate(selected,1):
        ax,ay=local(a,*p);bx,by=local(b,*q)
        edges.append(dict(id=i,a=dict(mapID=a,x=ax,y=ay),b=dict(mapID=b,x=bx,y=by),distance=math.dist(p,q),source='road-boundary' if (a,b) in recorded else 'dry-terrain-boundary'))
    structures=out/'structure-corridors.json'
    if structures.exists():
        for key,row in json.loads(structures.read_text()).items():
            edges.append(dict(id=len(edges)+1,a=row['a'],b=row['b'],distance=row['distance'],source=row['source'],structure=int(key)))
    report=dict(build=70959,maps=maps,aliases=aliases,crossings=edges,nativeFloorOnlyMaps=sorted(excluded),method='Native MCNK area ownership/AreaTable ancestry and UiMapAssignment. Road approaches within 62.5 yards with connectors up to 120 yards permitted in both masks; otherwise up to three independently dry boundary connectors per missing pair, ranked by connected ground and road proximity. Native structure corridors require separately validated floor proofs; underground city thresholds use these floors rather than ordinary terrain boundary extraction. Deduplicate outdoor connectors within 100 yards; Great Lift excluded pending transport support.')
    (out/'inventory.json').write_text(json.dumps(report,indent=2))
    def literal(value):
        if isinstance(value,dict):return '{'+','.join('['+literal(int(k) if str(k).isdigit() else k)+']='+literal(v) for k,v in value.items())+'}'
        if isinstance(value,list):return '{'+','.join(literal(v) for v in value)+'}'
        return json.dumps(value)
    text='-- Generated native outdoor crossings. See Crossings-SOURCES.md.\nlocal _,A=...\nA.CrossingData='+literal(dict(version=1,build=70959,maps=maps,aliases=aliases,edges=edges))+'\n'
    (ROOT/'Data/Crossings.lua').write_text(text,encoding='utf8')
    print('Crossings:',len(edges),'zone pairs:',len({tuple(sorted((e['a']['mapID'],e['b']['mapID']))) for e in edges if e['a']['mapID']!=e['b']['mapID']}),flush=True)
    for a,b,_,_ in selected:print(a,zones[a]['name'],'<->',b,zones[b]['name'])

if __name__=='__main__':main()
