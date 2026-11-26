"""Audit owned, dry playable approaches beyond every bundled handoff.

Read-only source checks; never creates routing permissions. Interior anchors
need floor-specific evidence rather than the root ground above/below them.
"""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]

def verify_inventory(raw,audit):
    if hashlib.sha256(raw).hexdigest()!=audit.get('inventorySha256'):
        raise ValueError('Stale approach evidence: rebuild the crossing approach audit after changing the inventory')

def area_owner(area,owners,parents):
    seen=set()
    while area and area not in seen:
        if area in owners:return owners[area]
        seen.add(area);area=parents.get(area,0)

def audit_side(origin,map_id,local,sample,owner,route,floor_height=None,away=None,fallback_route=None,extra_points=None):
    failures=Counter()
    try:ground=sample(*origin)
    except (ValueError,KeyError,FileNotFoundError,NotImplementedError):ground=None
    if floor_height is not None and (not ground or abs(ground['height']-floor_height)>.3):
        return dict(status='interior-floor-approach-required',floorHeight=floor_height,
                    rootGroundHeight=ground and ground['height'])
    start=local(*origin)
    # Small islands and narrow gate platforms may only have a short approach.
    groups=[[(r*math.cos(2*math.pi*i/16),r*math.sin(2*math.pi*i/16))for i in range(16)]for r in (150,75,30)]
    for group in range(len(groups)+(1 if extra_points else 0)):
        offsets=groups[group]if group<len(groups)else extra_points()
        for dn,de in offsets:
            radius=math.hypot(dn,de)
            if away and dn*away[0]+de*away[1]<-1e-6:continue
            n,e=origin[0]+dn,origin[1]+de
            try:g=sample(n,e)
            except (ValueError,KeyError,FileNotFoundError,NotImplementedError):
                failures['native source unavailable']+=1;continue
            if not g['permitted'] or g['liquid'] or g.get('hole'):
                failures['restricted or wet ground']+=1;continue
            if owner(g['area'])!=map_id:
                failures['different or unknown native owner']+=1;continue
            p=local(n,e)
            if not (0<=p['x']<=1 and 0<=p['y']<=1):
                failures['outside local artwork']+=1;continue
            for policy,planner in [('dry-only',route)]+([('swimming-fallback',fallback_route)]if fallback_route else []):
                forward,detail=planner(start,p)
                if not forward:failures[policy+': '+str(detail)]+=1;continue
                backward,detail=planner(p,start)
                if not backward:failures[policy+': '+str(detail)]+=1;continue
                status='verified-ground-approach'if policy=='dry-only'else'verified-with-swimming-fallback'
                if radius<75-1e-6:status='short-'+status
                return dict(status=status,point=p,world=[n,e,g['height']],policy=policy,
                            radius=radius,area=g['area'],distance=detail)
    return dict(status='unresolved-approach',failures=dict(failures))

def audit_border_approach(bank,other_bank,edges,by_id,world,allowed,ground,route):
    """Some bridges have only a short stretch of owned ground before a zone road."""
    origin=world(bank)
    opposite=world(other_bank)
    for edge in edges:
        if edge['source']!='road-boundary':continue
        for index,(here,there) in enumerate(((edge['a'],edge['b']),(edge['b'],edge['a']))):
            if here['mapID']!=bank['mapID'] or there['mapID']==here['mapID']:continue
            if math.dist(origin,world(here))>30:continue
            far=by_id[edge['id']]['sides'][1-index]
            if far['status']!='verified-ground-approach' or far['policy']!='dry-only':continue
            probe=far['point']
            end=world(probe)
            if math.dist(origin,end)<75 or probe['mapID']!=there['mapID']:continue
            if sum((v-o)*(o-b) for v,o,b in zip(end,origin,opposite))<=0:continue
            # Bind the short bank approach and crossing to dry native terrain and
            # both shipped terrain masks. Each probe retains its true UI map.
            a,b=world(here),world(there)
            if not allowed(bank['mapID'],origin,a) or not ground(origin,a,{here['mapID']}):continue
            if not all(allowed(z,a,b) for z in (here['mapID'],there['mapID'])) or not ground(a,b,{here['mapID'],there['mapID']}):continue
            walks=[]
            for start,finish in ((bank,here),(there,probe)):
                ok,detail=route(start,finish)
                if not ok or not route(finish,start)[0]:break
                walks.append(detail)
            if len(walks)!=2:continue
            return dict(status='verified-ground-approach-via-zone-crossing',point=probe,world=far['world'],
                        policy='dry-only',radius=math.dist(origin,end),area=far['area'],
                        distance=walks[0]+math.dist(a,b)+walks[1],
                        viaCrossing=dict(id=edge['id'],near=here,far=there,bankWalkYards=walks[0],
                                         crossingYards=math.dist(a,b),approachWalkYards=walks[1]))

def main():
    sys.path.insert(0,str(ROOT/'.test-deps'))
    from lupa.lua51 import LuaRuntime
    from bridge_geometry import Reader
    source=ROOT.parent/'output/forever-datamine-70959'
    db=source/'terrain-research/ashenvale/raw/dbfilesclient'
    def table(name):return list(csv.DictReader((db/(name+'.csv')).open(encoding='utf-8-sig')))
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones'] if z['type'] in (3,6) and 'wdt'in z}
    owners={int(r['AreaID']):int(r['UiMapID']) for r in table('uimapassignment') if int(r['UiMapID'])in zones and int(r['AreaID'])}
    owners={a:2521 if id==2665 else id for a,id in owners.items()}
    parents={int(r['ID']):int(r['ParentAreaID']) for r in table('areatable')}
    reader=Reader(source)
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
    for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/Water.lua','Data/WalkingRegions.lua','Data/Structures.lua','Terrain.lua','Water.lua','WalkingRegions.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text())
    lua.execute('A.InitStore({})')
    path=lua.eval('''function(a,b,swim)
      local points,why=A.Terrain.Path(a,b,{allowSwimming=swim,preferRoads=false,maxExpansions=6000,maxDistance=450})
      return points~=nil,why
    end''')
    segment=lua.eval('function(a,b)return A.Terrain.Segment(a,b,{allowSwimming=false}) end')
    reachable=lua.eval('''function(p)
      local z=A.Terrain.Zone(p.mapID);local w,h=z.w,z.h
      local x,y=math.min(w-1,math.floor(p.x*w)),math.min(h-1,math.floor(p.y*h))
      local function point(x,y)return {mapID=p.mapID,x=(x+.5)/w,y=(y+.5)/h}end
      local first=point(x,y);local result={};local seen={[y*w+x]=true};local q={{x,y}};local at=1
      if not A.Terrain.Segment(p,first,{allowSwimming=true})then return result end
      while at<=#q and at<=6000 do
        local c=q[at];at=at+1;local a=point(c[1],c[2])
        local dx,dy=(a.x-p.x)*z.widthYards,(a.y-p.y)*z.heightYards
        if dx*dx+dy*dy>=75*75 then result[#result+1]={dx,dy}end
        for _,d in ipairs({{1,0},{-1,0},{0,1},{0,-1}})do
          local nx,ny=c[1]+d[1],c[2]+d[2];local id=ny*w+nx
          local b=point(nx,ny);local ex,ey=(b.x-p.x)*z.widthYards,(b.y-p.y)*z.heightYards
          if nx>=0 and ny>=0 and nx<w and ny<h and not seen[id]and ex*ex+ey*ey<=450*450 then
            seen[id]=true
            if A.Terrain.Segment(a,b,{allowSwimming=true})then q[#q+1]={nx,ny}end
          end
        end
      end
      return result
    end''')
    inventory_raw=(ROOT.parent/'output/zone-crossings-70959/inventory.json').read_bytes()
    inventory=json.loads(inventory_raw)
    results=[]
    for edge in inventory['crossings']:
        row=dict(id=edge['id'],source=edge['source'],structure=edge.get('structure'),sides=[])
        structure=lua.globals().A.StructureData.corridors[edge.get('structure',0)]
        for side in ('a','b'):
            p=edge[side];z=zones[p['mapID']];other=edge['b'if side=='a'else'a']
            n=z['north']-p['y']*(z['north']-z['south']);e=z['west']-p['x']*(z['west']-z['east'])
            sampler=reader.sampler(z['terrainMap'],z['wdt'])
            def local(n,e):return dict(mapID=p['mapID'],x=(z['west']-e)/(z['west']-z['east']),y=(z['north']-n)/(z['north']-z['south']))
            def route(a,b):return path(lua.table_from(a),lua.table_from(b),False)
            def fallback(a,b):return path(lua.table_from(a),lua.table_from(b),True)
            floor_height=None
            if structure:
                if structure.worldPath:
                    floor_height=structure.worldPath[1 if side=='a' else len(structure.worldPath)][3]
                elif structure.heightProfile:
                    floor_height=structure.heightProfile[1 if side=='a' else len(structure.heightProfile)][2]
            away=None
            if other['mapID']==p['mapID']:
                away=(n-(z['north']-other['y']*(z['north']-z['south'])),e-(z['west']-other['x']*(z['west']-z['east'])))
            def extra():
                return [(-v[2],-v[1])for _,v in reachable(lua.table_from(p)).items()]
            result=audit_side((n,e),p['mapID'],local,lambda n,e:reader.terrain(sampler,n,e),
                              lambda a:area_owner(a,owners,parents),route,floor_height,away,fallback,extra)
            row['sides'].append(dict(side=side,mapID=p['mapID'],**result))
        results.append(row)
        print('Approach',edge['id'],*[s['status']for s in row['sides']],flush=True)
    by_id={r['id']:r for r in results}
    def world(p):
        z=zones[p['mapID']]
        return z['north']-p['y']*(z['north']-z['south']),z['west']-p['x']*(z['west']-z['east'])
    def allowed(map_id,a,b):
        z=zones[map_id]
        def point(p):
            return lua.table_from(dict(mapID=map_id,x=(z['west']-p[1])/(z['west']-z['east']),y=(z['north']-p[0])/(z['north']-z['south'])))
        start,finish=point(a),point(b)
        return segment(start,finish) and segment(finish,start)
    for edge in inventory['crossings']:
        if not edge.get('structure') or edge['a']['mapID']!=edge['b']['mapID']:continue
        for side in by_id[edge['id']]['sides']:
            if side['status']!='unresolved-approach':continue
            bank=edge[side['side']];other=edge['b' if side['side']=='a' else 'a']
            z=zones[bank['mapID']];sampler=reader.sampler(z['terrainMap'],z['wdt'])
            def ground(a,b,expected):
                count=max(1,math.ceil(math.dist(a,b)))
                for i in range(count+1):
                    n,e=[v+(w-v)*i/count for v,w in zip(a,b)]
                    try:g=reader.terrain(sampler,n,e)
                    except (ValueError,KeyError,FileNotFoundError,NotImplementedError):return False
                    if not g['permitted'] or area_owner(g['area'],owners,parents) not in expected:return False
                return True
            combined=audit_border_approach(bank,other,inventory['crossings'],by_id,world,allowed,ground,
                                           lambda a,b:path(lua.table_from(a),lua.table_from(b),False))
            if combined:
                side.update(combined)
                side['localProbeFailures']=side.pop('failures')
                print('Approach',edge['id'],side['side'],'via crossing',combined['viaCrossing']['id'],flush=True)
    counts=Counter(s['status']for row in results for s in row['sides'])
    out=ROOT/'tools/data/crossing-approaches-manifest.json'
    out.write_text(json.dumps(dict(build=70959,liveStatus='not-tested',normalApproachYards=75,shortApproachYards=30,
        inventorySha256=hashlib.sha256(inventory_raw).hexdigest(),crossingDataSha256=hashlib.sha256((ROOT/'Data/Crossings.lua').read_bytes()).hexdigest(),
        counts=dict(counts),links=results,sourceHashes={str(k):v for k,v in sorted(reader.hashes.items())}),indent=2)+'\n')
    maps=inventory['maps'];lines=['# Crossing approach audit','',
        'Source build 70959; live client acceptance is separate. Generated by `python tools/audit_crossing_approaches.py`.','',
        'The usual ground probe lies on dry native ground owned by the handoff zone at least 75 yards away, with shipped routing in both directions. Most probes cover 75–150 yards and connected-grid probes can extend to 450 yards. Short approaches cover 30 yards. Swimming-fallback results permit swimming or coarse liquid cells along the route. Same-zone bridge probes extend away from the other bank. The checks sample ground and floor geometry.','',
        ', '.join(f'**{v} {k}**'for k,v in sorted(counts.items()))+'.','',
        'A bridge beside a zone road can have its outward ground probe in the adjoining zone. These rows identify the intervening crossing in the manifest and validate the dry bank walk, the crossing in both terrain masks, and the adjacent-zone ground walk in both directions.','',
        '| Link | Zones | Side A | Side B |','| --- | --- | --- | --- |']
    for row in results:
        names=' / '.join(maps[str(s['mapID'])]['name']for s in row['sides'])
        lines.append(f"| {row['id']} | {names} | {row['sides'][0]['status']} | {row['sides'][1]['status']} |")
    lines+=['','Interior-floor results require the existing native floor evidence and live confirmation; root terrain cannot prove a route inside a capital or cave. Unresolved results are retained with rejection reasons in the manifest and never create guessed links.','']
    (ROOT/'docs/crossing-approaches-audit.md').write_text('\n'.join(lines),encoding='utf8')
    print(dict(counts))
if __name__=='__main__':main()
