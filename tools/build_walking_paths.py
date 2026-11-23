"""Compile fixed travel-point walking geometry with the unchanged Lua 5.1 search.

Missing pairs and bounded offline failures deliberately remain live searches.
Run --inventory to inspect coverage before doing the offline work.
"""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import math
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'))
from lupa.lua51 import LuaRuntime

INPUTS=['Data/Terrain.lua','Data/Water.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua',
        'Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua',
        'Data/HarbourAccess.lua','Data/Flights.lua','Data/Transports.lua',
        'Data/LocalTransports.lua','Roads.lua','Water.lua','Terrain.lua','WalkingRegions.lua','PathReuse.lua']

def runtime():
    lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={}')
    for name in INPUTS:
        lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/name).read_text(encoding='utf8'))
    return lua

def plain(value):
    if hasattr(value,'items'):
        values=dict(value.items())
        if values and set(values)==set(range(1,len(values)+1)):
            return [plain(values[i]) for i in range(1,len(values)+1)]
        return {k:plain(v) for k,v in values.items()}
    return value

def anchors(lua):
    rows=lua.eval('''function()
      local rows={}
      local function add(p,kind)
        if p and A.Terrain.Zone(p.mapID) and A.Terrain.Segment(p,p) then
          rows[#rows+1]={mapID=p.mapID,x=p.x,y=p.y,kind=kind}
        end
      end
      for _,e in ipairs(A.CrossingData.edges) do add(e.a,'crossing');add(e.b,'crossing') end
      for _,node in pairs(A.FlightData.nodes) do if node.destinationAvailable then add(node.a,'flight') end end
      for _,d in ipairs({A.TransportData,A.LocalTransportData}) do
        for _,e in ipairs(d.edges) do add(e.a,e.kind);add(e.b,e.kind) end
      end
      -- Ground ends of proven dock corridors, not straight chords under piers.
      for _,e in pairs(A.HarbourAccessData.corridors) do add(e.a,'dock-ground') end
      return rows
    end''')()
    zones={}
    for row in plain(rows):
        m=row.pop('mapID');key=(row['x'],row['y'])
        zones.setdefault(m,{})[key]=row
    return {m:[dict(mapID=m,x=x,y=y,kind=points[x,y]['kind'])
               for x,y in sorted(points)] for m,points in sorted(zones.items())}

def pairs_for(points,max_pairs):
    # Favor each anchor's nearby neighbors, then longer pairs. Never create
    # artificial graph links: these are lookup accelerators, not new exits.
    all_pairs=[]
    for i,a in enumerate(points):
        ranked=sorted((math.hypot(a['x']-b['x'],a['y']-b['y']),j)
                      for j,b in enumerate(points) if i!=j)
        ranks={j:k for k,(_,j) in enumerate(ranked)}
        for j in range(i+1,len(points)):
            all_pairs.append((ranks[j],math.hypot(a['x']-points[j]['x'],a['y']-points[j]['y']),i,j))
    selected=sorted(all_pairs)[:max_pairs] if max_pairs else all_pairs
    return [(points[i],points[j]) for _,_,i,j in selected]

def compile_zone(task):
    map_id,points,max_pairs,budget=task
    lua=runtime();a=lua.globals().A;groups={};failed=0
    pairs=pairs_for(points,max_pairs)
    for strength in range(6):
        options=lua.table_from(dict(preferRoads=strength>0,roadPreferenceStrength=strength,maxExpansions=budget))
        signature,mode=a.PathReuse.Signature(map_id,options)
        # A zone without effective roads has the same mode in every setting.
        if mode in groups:continue
        paths={}
        for first,last in pairs:
            p,q=lua.table_from(first),lua.table_from(last)
            if a.WalkingRegions.Get(p)!=a.WalkingRegions.Get(q):failed+=1;continue
            result=a.PathReuse.OriginalPath(p,q,options)
            path,length=result if isinstance(result,tuple) else (result,None)
            if path is None:failed+=1;continue
            if len(path)>2048:failed+=1;continue
            assert a.Terrain.Validate(lua.table_from(dict(points=path)))
            key,reverse=a.PathReuse.Key(p,q)
            geometry=plain(path)
            if reverse:geometry.reverse()
            paths[key]=dict(points=geometry,length=length)
        if paths:groups[mode]=dict(signature=signature,paths=dict(sorted(paths.items())))
    return map_id,groups,failed,len(pairs)

def literal(value):
    if isinstance(value,dict):return '{'+','.join('['+literal(k)+']='+literal(v) for k,v in sorted(value.items(),key=lambda item:str(item[0])))+'}'
    if isinstance(value,list):return '{'+','.join(literal(v) for v in value)+'}'
    return json.dumps(value,allow_nan=False,separators=(',',':'))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--max-pairs',type=int,default=32,help='per-zone pair cap; 0 means all pairs')
    parser.add_argument('--budget',type=int,default=262144)
    parser.add_argument('--inventory',action='store_true')
    parser.add_argument('--revalidate-existing',action='store_true',help='retain generated geometry only when every allowed-mode input signature and segment still validates; do not claim a fresh search')
    args=parser.parse_args();zones=anchors(runtime())
    if args.revalidate_existing:
        lua=runtime();path=ROOT/'Data/WalkingPaths.lua'
        lua.execute('assert(loadstring(...))("Mapperly",A)',path.read_text())
        count=lua.execute('''
          local count=0
          for map,zone in pairs(A.WalkingPathData.zones) do for mode,group in pairs(zone) do
            local options={allowSwimming=true,preferRoads=mode>0,roadPreferenceStrength=mode}
            assert(A.PathReuse.Signature(map,options)==group.signature,'Changed allowed-mode signature: '..map)
            for key,entry in pairs(group.paths) do
              assert(A.Terrain.Validate({points=entry.points},options),'Invalid retained path: '..key)
              count=count+1
            end
          end end
          return count
        ''')
        manifest_path=ROOT/'tools/data/walking-paths-manifest.json';manifest=json.loads(manifest_path.read_text())
        assert count==manifest['paths'] and hashlib.sha256(path.read_bytes()).hexdigest()==manifest['outputSha256']
        prior=manifest['inputs']
        manifest['inputs']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in INPUTS}
        manifest['revalidation']=dict(method='Retained original allowed-mode search geometry: every resolved revision-1 signature unchanged and every segment validated with explicit allowSwimming=true. No new optimality/search claim.',paths=count,previousInputs=prior)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'Revalidated {count} unchanged allowed-mode paths; all signatures and segments match');return
    tasks=[(m,points,args.max_pairs,args.budget) for m,points in zones.items() if len(points)>1]
    if args.inventory:
        print(json.dumps({m:dict(anchors=len(p),pairs=len(pairs_for(p,args.max_pairs))) for m,p,_,_ in tasks},indent=2));return
    started=time.perf_counter();compiled={};failures=0;pair_count=0
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for map_id,groups,failed,pairs in pool.map(compile_zone,tasks):
            if groups:compiled[map_id]=groups
            failures+=failed;pair_count+=pairs
            count=sum(len(g['paths']) for g in groups.values())
            print(f'{map_id}: {count} paths, {failed} live-fallback cases',flush=True)
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in INPUTS}
    data=dict(version=1,revision=1,zones=compiled)
    path=ROOT/'Data/WalkingPaths.lua'
    path.write_text('-- Generated by tools/build_walking_paths.py; see WalkingPaths-SOURCES.md.\nlocal _,A=...\nA.WalkingPathData='+literal(data)+'\n',encoding='utf8')
    count=sum(len(g['paths']) for z in compiled.values() for g in z.values())
    point_count=sum(len(p['points']) for z in compiled.values() for g in z.values() for p in g['paths'].values())
    manifest=dict(version=1,revision=1,inputs=hashes,maxPairs=args.max_pairs,budget=args.budget,
                  zones=len(compiled),pairs=pair_count,paths=count,points=point_count,failed=failures,
                  outputSha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (ROOT/'tools/data/walking-paths-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print(f'{count} paths/{point_count} points in {len(compiled)} zones; {path.stat().st_size} bytes; {time.perf_counter()-started:.1f}s',flush=True)

if __name__=='__main__':main()
