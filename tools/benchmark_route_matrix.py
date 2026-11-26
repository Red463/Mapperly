"""Sequential, reproducible route latency survey; never changes routing data.

Run --prepare, then --run. Each cold/warm pair owns a fresh Lua 5.1 runtime.
Host computation and a 60fps scheduling model are distinct from live timings.
"""
from pathlib import Path
from collections import deque,Counter
import argparse,csv,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/route-matrix-2026-11-25'
FILES=['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua',
 'Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua','Data/Structures.lua',
 'Data/HarbourAccess.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/Trams.lua',
 'Data/Flights.lua','Data/WalkingPaths.lua','Roads.lua','Data/Water.lua','Water.lua',
 'Data/WalkingPortals.lua','TerrainPortals.lua','Terrain.lua','PathReuse.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua',
 'TravelBounds.lua','TravelNetwork.lua','Flights.lua','Transports.lua','Trams.lua',
 'CityNavigation.lua','Journey.lua']
TOWNS=[
 ('Goldshire',1429,42.3,66.6,'Alliance'),('Eastvale',1429,83.7,69.4,'Alliance'),
 ('Sentinel Hill',1436,56,47,'Alliance'),('Darkshire',1431,77,44,'Alliance'),
 ('Lakeshire',1433,26.6,44.7,'Alliance'),('Stormwind',1453,62.4,72,'Alliance'),
 ('Kharanos',1426,46,51,'Alliance'),('Thelsamar',1432,35.1,48.5,'Alliance'),
 ('Menethil',1437,10.6,60.8,'Alliance'),('Southshore',1424,50.5,58.3,'Alliance'),
 ('Refuge Pointe',1417,45.9,46.1,'Alliance'),('Aerie Peak',1425,11.5,46.2,'Alliance'),
 ('Chillwind',1422,43,85,'Alliance'),('Lights Hope',1423,75.6,53.5,'Alliance'),
 ('Booty Bay',1434,27.2,76.9,'Neutral'),('Auberdine',1439,36.5,45.6,'Alliance'),
 ('Astranaar',1440,34,48,'Alliance'),('Ashenvale east',1440,85.2,44.6,'Alliance'),
 ('Azshara bank',1447,10.57,75.08,'Neutral'),('Ratchet',1413,62.4,37.8,'Neutral'),
 ('Theramore',1445,67.5,51.2,'Alliance'),('Gadgetzan',1446,51.8,28.5,'Neutral'),
 ('Marshals Refuge',1449,45,5.7,'Neutral'),('Cenarion Hold',1451,51.2,38.4,'Neutral'),
 ('Emerald Sanctuary',1448,51.1,82.2,'Neutral'),('Everlook',1452,61.3,38.8,'Neutral'),
 ('Moonglade',1450,52,59,'Neutral'),('Feathermoon',1444,30,43,'Alliance'),
 ('Crossroads',1413,51.9,30.3,'Horde'),('Razor Hill',1411,52,43.5,'Horde'),
 ('Orgrimmar',1454,50.5,65.4,'Horde'),('Bloodhoof',1412,47,61,'Horde'),
 ('Camp Mojache',1444,75.9,44.7,'Horde'),('Sun Rock',1442,45,59,'Horde'),
 ('Shadowprey',1443,22.8,72,'Horde'),('Brill',1420,61,52,'Horde'),
 ('Sepulcher',1421,45,43,'Horde'),('Tarren Mill',1424,62,20,'Horde'),
 ('Shimmering Flats',1441,78,75,'Neutral')]

def plain(v):
    if hasattr(v,'items'):
        d=dict(v.items())
        if d and set(d)==set(range(1,len(d)+1)):return [plain(d[i])for i in range(1,len(d)+1)]
        return {str(k):plain(x)for k,x in d.items()}
    return v

def runtime(faction='Alliance',profile='off',flights=False,avoid=False):
    sys.path.insert(0,str(ROOT/'.test-deps'))
    from lupa.lua51 import LuaRuntime
    l=LuaRuntime(unpack_returned_tuples=True)
    l.execute((ROOT/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
    for f in FILES:l.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text(encoding='utf8'))
    g=l.globals();g.benchClock=lambda:time.perf_counter()*1000
    g.benchSide=faction;g.benchRoads=profile!='off';g.benchStrength={'off':3,'light':1,'moderate':2,'normal':3,'firm':4,'strong':5}[profile];g.benchAvoid=avoid
    l.execute('''
      debugprofilestop=benchClock
      GetTimePreciseSec=function()return benchClock()/1000 end
      UnitClass=function()return 'Warrior','WARRIOR',1 end
      UnitFactionGroup=function()return benchSide end
      UnitGUID=function()return 'Player-1-Matrix' end
      UnitOnTaxi=function()return false end;UnitInVehicle=function()return false end
      GetMoney=function()return 100000000 end
      A.InitStore({preferRoads=benchRoads,roadPreferenceStrength=benchStrength,avoidSwimming=benchAvoid})
    ''')
    if flights:
        # Synthetic character: recorded offers only through native directed
        # segment chains, between these named hubs. Not the user's unlocks.
        l.execute('''
          local c=A.Flights.Character();local hubs=benchSide=='Alliance'and{2,4,6,7,12,14,18,26,28,32}or{19,23,25,80}
          for _,id in ipairs(hubs)do c.nodes[id]=true end
          for _,source in ipairs(hubs)do
            local scores,previous,closed={[source]=0},{},{}
            for iteration=1,500 do
              local at,best;for id,cost in pairs(scores)do if not closed[id]and(not best or cost<best)then at,best=id,cost end end
              if not at then break end;closed[at]=true
              for key,s in pairs(A.FlightData.segments)do
                local from,to=key:match('^(%d+):(%d+)$');from,to=tonumber(from),tonumber(to)
                local node=A.FlightData.nodes[to];local mask=node and node.factionMask
                local allowed=mask and node.eligible~=false and(not node.classToken or node.classToken=='WARRIOR')and(benchSide=='Alliance'and mask%2==1 or benchSide=='Horde'and math.floor(mask/2)%2==1)
                if from==at and allowed and not closed[to]and(not scores[to]or best+(s.seconds or 1)<scores[to])then scores[to]=best+(s.seconds or 1);previous[to]=at end
              end
            end
            c.offers[source]={}
            for _,target in ipairs(hubs)do if target~=source and previous[target]then
              local hops={target};local at=target;while at~=source do at=previous[at];table.insert(hops,1,at)end
              c.offers[source][target]={from=source,to=target,hops=hops}
            end end
          end
        ''')
    return l

def prepare():
    OUT.mkdir(parents=True,exist_ok=True);l=runtime();A=l.globals().A
    graph={};names={}
    for id,m in A.CrossingData.maps.items():names[int(id)]=m.name
    for _,e in A.CrossingData.edges.items():
        if e.a.mapID!=e.b.mapID:
            graph.setdefault(int(e.a.mapID),set()).add(int(e.b.mapID));graph.setdefault(int(e.b.mapID),set()).add(int(e.a.mapID))
    def chain(a,b):
        q=deque([[a]]);seen={a}
        while q:
            p=q.popleft()
            if p[-1]==b:return p
            for n in sorted(graph.get(p[-1],[])):
                if n not in seen:seen.add(n);q.append(p+[n])
    anchors={};rejected=[]
    for name,id,x,y,side in TOWNS:
        raw=dict(mapID=id,x=x/100,y=y/100);p=l.table_from(raw)
        if A.CityNavigation.Supports(p):point=raw
        else:
            q=A.Terrain.Approach(p,60)
            if isinstance(q,tuple):q=q[0]
            if q is None:rejected.append(dict(name=name,point=raw,reason='No permitted point within 60 yards'));continue
            point=plain(q)
        dist=A.TravelNetwork.Distance(p,l.table_from(point))
        anchors[name]=dict(name=name,point=point,raw=raw,adjustmentYards=dist,side=side,zone=names[id],instance=int(A.CrossingData.maps[id].instance))
    cases=[];used=set()
    def add(a,b,kind=None):
        if a not in anchors or b not in anchors:return
        x,y=anchors[a],anchors[b];path=chain(x['point']['mapID'],y['point']['mapID'])
        if (a,b)in used:return
        used.add((a,b));cases.append(dict(id=f'R{len(cases)+1:02}',start=x,goal=y,category=kind or str(len(path)if path else 'no-walking-link'),
            minimumWalkingZoneCount=len(path)if path else None,minimumWalkingChain=path,
            faction='Horde'if 'Horde'in(x['side'],y['side'])else'Alliance'))
    for a,b in [('Goldshire','Eastvale'),('Astranaar','Ashenvale east'),('Razor Hill','Orgrimmar'),('Goldshire','Darkshire'),('Darkshire','Kharanos'),('Ashenvale east','Azshara bank')]:add(a,b)
    usage=Counter()
    for bucket in ['2','3','4','5','6','7','8+']:
        for instance in (0,1):
            candidates=[]
            for a,x in anchors.items():
                for b,y in anchors.items():
                    if 'Shimmering Flats'in(a,b):continue # user case is appended without changing prior route IDs
                    if a>=b or x['instance']!=instance or y['instance']!=instance or {x['side'],y['side']}=={'Alliance','Horde'}:continue
                    path=chain(x['point']['mapID'],y['point']['mapID'])
                    n=len(path)if path else 0
                    if not (n>=8 if bucket=='8+'else n==int(bucket)):continue
                    if (a,b)in used or(b,a)in used:continue
                    candidates.append((a,b))
            for repeat in range(2):
                if not candidates:break
                a,b=min(candidates,key=lambda p:(usage[p[0]]+usage[p[1]],p));candidates.remove((a,b));add(a,b,bucket);usage[a]+=1;usage[b]+=1
    for a,b in [('Auberdine','Menethil'),('Menethil','Auberdine'),('Astranaar','Goldshire'),('Goldshire','Astranaar'),('Ratchet','Booty Bay'),('Orgrimmar','Brill'),('Ashenvale east','Menethil')]:add(a,b,'cross-continent')
    add('Ratchet','Shimmering Flats','user-route')
    meta=dict(created='2026-11-25',version='1.2.5 working tree',host=platform.platform(),python=sys.version,
        methodology='Each pair has fresh Lua 5.1 state plus shipped paths; immediate repeat retains only that pair. Transport methods enabled. No flights recorded unless explicitly flagged. Town anchors may move at most 60 yards onto permitted terrain; exact tested coordinates and movement are retained. Minimum zone counts are walking-graph counts including both endpoints; actual plans may use more zones, trams, flights or boats.',
        sourceHashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest()for f in FILES},anchors=anchors,rejectedAnchors=rejected,cases=cases)
    (OUT/'matrix.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Prepared',len(cases),'routes',dict(Counter(x['category']for x in cases)),'rejected anchors',rejected)

def worker(case,profile,flights,avoid,limit,walking=False,trace=False):
    l=runtime(case['faction'],profile,flights,avoid);A=l.globals().A
    start=l.table_from(case['start']['point']);goal=l.table_from(case['goal']['point']);l.globals().benchStart=start;l.globals().benchGoal=goal
    l.globals().benchOptions=l.table_from(dict(faction=case['faction'],liveStart=True,walkingOnly=walking))
    if trace:l.execute('''
      local original=A.Terrain.Path
      A.Terrain.Path=function(a,b,o)
        local started=benchClock();local p=A.PlanningJob.Progress();local cells=p and p.cells or 0
        local points,length=original(a,b,o);p=A.PlanningJob.Progress()
        benchTrace[#benchTrace+1]={mapID=a.mapID,ax=a.x,ay=a.y,bx=b.x,by=b.y,
          seconds=(benchClock()-started)/1000,cells=(p and p.cells or cells)-cells,
          status=points and 'ok'or tostring(length),distance=points and length or nil}
        return points,length
      end
    ''')
    l.execute('''function benchBegin()
      benchResult=nil;benchError=nil;benchProgress=nil;benchTrace={}
      A.PlanningJob.Start(function()
        local p,why=A.Journey.Plan(benchStart,benchGoal,benchOptions)
        benchProgress=A.PlanningJob.Progress();return p,why
      end,function(p)benchResult=p end,function(why)benchError=why end)
    end''')
    rows=[]
    for temperature in ('cold','warm'):
        before=plain(A.PathReuse.Stats());l.globals().benchBegin();began=time.perf_counter();slices=0;max_step=0;model=0;progress={};timeout=False
        while A.PlanningJob.IsRunning():
            t=time.perf_counter();A.PlanningJob.Step();dt=time.perf_counter()-t;slices+=1;max_step=max(max_step,dt);model+=max(1/60,dt)
            p=A.PlanningJob.Progress()
            if p:progress=plain(p)
            if time.perf_counter()-began>limit:timeout=True;A.PlanningJob.Cancel();break
        elapsed=time.perf_counter()-began;p=l.globals().benchResult
        if l.globals().benchProgress:progress=plain(l.globals().benchProgress)
        after=plain(A.PathReuse.Stats());row=dict(case=case['id'],profile=profile,flights=flights,avoidSwimming=avoid,walkingOnly=walking,temperature=temperature,
            status='timeout'if timeout else'ok'if p else'failed',reason=str(l.globals().benchError)if l.globals().benchError else None,
            hostSeconds=round(elapsed,4),modeled60fpsSeconds=round(max(0,model-1/60+dt),4),slices=slices,maxStepMS=round(max_step*1000,3),progress=progress,
            pathReuseDelta={k:after.get(k,0)-before.get(k,0)for k in ('hits','bakedHits','failureHits','misses')},flightStats=list(A.Flights.Stats()))
        if p:
            zones=[];vehicles=[];invalid=[];guidance=[]
            for _,leg in p.legs.items():
                if leg.kind=='walk':
                    if not zones or zones[-1]!=leg.mapID:zones.append(int(leg.mapID))
                    if leg.cityGuidance or leg.portalGuidance:guidance.append(int(leg.mapID))
                    else:
                        valid=A.Terrain.Validate(leg)
                        if isinstance(valid,tuple):valid=valid[0]
                        if not valid:invalid.append(int(leg.mapID))
                elif leg.transport:vehicles.append(dict(kind=leg.transport.kind,name=leg.transport.name,id=leg.transport.id))
            row.update(distanceYards=p.distance,journeySeconds=p.estimatedSeconds,coverage=p.coverage,swimmingFallback=bool(p.swimmingFallback),swimmingFallbackReason=p.swimmingFallbackReason,actualZones=zones,vehicles=vehicles,invalidWalkingLegs=invalid,approximateGuidanceZones=guidance)
            if invalid:row['status']='invalid-geometry'
        if trace:row['trace']=plain(l.globals().benchTrace)
        rows.append(row)
    print(json.dumps(rows),flush=True)

def run(args):
    matrix=json.loads((OUT/'matrix.json').read_text());cases=matrix['cases']
    if args.cases:cases=[c for c in cases if c['id']in args.cases.split(',')]
    output=OUT/(args.label+'.jsonl')
    with output.open('w')as stream:
        for case in cases:
            for profile in args.profiles.split(','):
                cmd=[sys.executable,__file__,'--worker',case['id'],'--profile',profile,'--limit',str(args.limit)]
                if args.flights:cmd.append('--flights')
                if args.avoid:cmd.append('--avoid')
                if args.walking:cmd.append('--walking')
                if args.trace:cmd.append('--trace')
                try:
                    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=args.limit*2+25)
                    if p.returncode:rows=[dict(case=case['id'],profile=profile,flights=args.flights,avoidSwimming=args.avoid,status='harness-error',reason=p.stderr[-1800:])]
                    else:rows=json.loads(p.stdout)
                except subprocess.TimeoutExpired:rows=[dict(case=case['id'],profile=profile,flights=args.flights,avoidSwimming=args.avoid,status='process-timeout',reason='Parent safety timeout')]
                for row in rows:stream.write(json.dumps(row)+'\n');stream.flush()
                print(case['id'],case['category'],case['start']['name']+' -> '+case['goal']['name'],profile,
                    [(r.get('temperature'),r['status'],r.get('hostSeconds'),r.get('modeled60fpsSeconds'),r.get('progress',{}).get('cells'))for r in rows],flush=True)
    print('Saved',output,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');parser.add_argument('--run',action='store_true');parser.add_argument('--worker');parser.add_argument('--profile',default='off');parser.add_argument('--profiles',default='off,firm');parser.add_argument('--cases');parser.add_argument('--flights',action='store_true');parser.add_argument('--avoid',action='store_true');parser.add_argument('--walking',action='store_true');parser.add_argument('--trace',action='store_true');parser.add_argument('--limit',type=float,default=45);parser.add_argument('--label',default='primary');args=parser.parse_args()
    if args.prepare:prepare()
    if args.worker:
        matrix=json.loads((OUT/'matrix.json').read_text());worker(next(c for c in matrix['cases']if c['id']==args.worker),args.profile,args.flights,args.avoid,args.limit,args.walking,args.trace)
    if args.run:run(args)
