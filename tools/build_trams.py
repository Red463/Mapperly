"""Bundle Deeprun's fixed native service; no player recordings or addon data."""
from pathlib import Path
import csv,hashlib,json,math,sys
from build_services import rows,CACHE,WORLD
ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lua(v):
 if isinstance(v,dict):return '{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
 if isinstance(v,list):return '{'+','.join(lua(x)for x in v)+'}'
 if isinstance(v,bool):return 'true'if v else 'false'
 return json.dumps(v)
def build():
 portals=json.loads((ROOT/'tools/data/native-tram-portals-70959.json').read_text(encoding='utf8'))
 floor_path=ROOT/'tools/data/native-tram-exits-70959.json';floors=json.loads(floor_path.read_text(encoding='utf8'))
 source=CACHE/WORLD;sha=digest(source)
 assert portals['sourceSha256']==floors['sourceSha256']==sha
 templates={};spawns={}
 entries=set(range(176080,176086))
 for table,r in rows(source,{'gameobject_template','gameobject'}):
  if table=='gameobject_template'and int(r['entry'])in entries:templates[int(r['entry'])]=r
  elif table=='gameobject'and int(r['id'])in entries and int(r['map'])==369:spawns[int(r['id'])]=r
 assert set(templates)==set(spawns)==entries
 for r in templates.values():assert r['type']=='11'and r['name']=='Subway'
 animation=ROOT/'output/tram-audit/transportanimation.csv'
 native={entry:[]for entry in entries}
 for r in csv.DictReader(animation.open(encoding='utf8')):
  entry=int(r['TransportID'])
  if entry in native:native[entry].append(r)
 for entry,points in native.items():
  assert len(points)>2 and max(int(r['TimeIndex'])for r in points)==143333
  assert max(float(r['Pos[1]'])for r in points)-min(float(r['Pos[1]'])for r in points)>2400
 zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
 exits={r['mapID']:r for r in floors['exits']};assert set(exits)=={1453,1455}
 destinations={r['triggerID']:r['destination']for r in portals['portals']}
 triggers={}
 for r in csv.DictReader((ROOT/'output/tram-audit/areatrigger.csv').open()):
  if int(r['ID'])in{2173,2175}:triggers[int(r['ID'])]=r
 def point(mid,n,e):
  z=zones[mid];return dict(mapID=mid,x=(z['west']-e)/(z['west']-z['east']),y=(z['north']-n)/(z['north']-z['south']))
 def world(n,e):return dict(worldX=e,worldY=n,instance=0)
 data=[]
 for source_map,target_map,entry_trigger,exit_trigger,from_name,to_name in [(1453,1455,2173,2166,'Stormwind','Ironforge'),(1455,1453,2175,2171,'Ironforge','Stormwind')]:
  entry=triggers[entry_trigger];exit=exits[target_map];destination=destinations[exit_trigger]
  assert int(entry['ContinentID'])==0 and destinations[entry_trigger]['continent']==369
  assert exit['exitTriggerID']==exit_trigger and destination['continent']==0
  for axis in ('north','east','z'):assert abs(exit[axis]-destination[axis])<.001
  assert exit['heightError']<.001 and abs(exit['groundHeight']-exit['z'])<.001
  # Independently recompute the selected native triangle's supported floor.
  va,vb,vc=exit['vertices'];pn,pe=exit['north'],exit['east']
  den=(vb[1]-vc[1])*(va[0]-vc[0])+(vc[0]-vb[0])*(va[1]-vc[1]);assert abs(den)>1e-9
  u=((vb[1]-vc[1])*(pn-vc[0])+(vc[0]-vb[0])*(pe-vc[1]))/den
  v=((vc[1]-va[1])*(pn-vc[0])+(va[0]-vc[0])*(pe-vc[1]))/den
  assert min(u,v,1-u-v)>=-1e-6
  height=u*va[2]+v*vb[2]+(1-u-v)*vc[2];assert abs(height-exit['groundHeight'])<1e-5
  assert len(exit['rootSha256'])==len(exit['groupSha256'])==64
  n,e=float(entry['Pos[0]']),float(entry['Pos[1]'])
  data.append(dict(id=f'tram:deeprun:{source_map}:{target_map}',kind='tram',automaticTram=True,name='Deeprun Tram',faction='Neutral',
   a=point(source_map,n,e),b=point(target_map,exit['north'],exit['east']),board=world(n,e),arrival=world(exit['north'],exit['east']),
   boardingGroundHeight=exits[source_map]['groundHeight'],arrivalGroundHeight=exit['groundHeight'],
   fromName=from_name,toName=to_name,interiorInstance=369,entryTriggerID=entry_trigger,exitTriggerID=exit_trigger,
   planningSeconds=264,waitAssumptionSeconds=72,rideEstimateSeconds=72,stationAccessEstimateSeconds=120,timingIsAssumption=True))
 service=dict(version=1,build=70959,source=WORLD,sourceSha256=sha,portalSourceSha256=digest(ROOT/'tools/data/native-tram-portals-70959.json'),
  floorSourceSha256=digest(floor_path),animationCsvSha256=digest(animation),nativeCycleMS=143333,
  templates=[dict(entry=i,type=int(templates[i]['type']),displayID=int(templates[i]['displayId']),name=templates[i]['name'])for i in sorted(entries)],
  spawns=[dict(entry=i,guid=int(spawns[i]['guid']),instance=369,north=float(spawns[i]['position_x']),east=float(spawns[i]['position_y']),z=float(spawns[i]['position_z']))for i in sorted(entries)],
  method='Pinned native SQL Subway type11 templates/spawns, native143333ms animation, paired portal safe locations and exact native WMO exit floors. Planning allowance includes estimated station access; not a timetable.',edges=data)
 proof=ROOT/'tools/data/native-tram-service-70959.json';proof.write_text(json.dumps(service,indent=2)+'\n',encoding='utf8')
 result=dict(version=1,build=70959,sourceSha256=digest(proof),floorSourceSha256=digest(floor_path),edges=data)
 (ROOT/'Data/Trams.lua').write_text('-- Fixed native Deeprun service; see Trams-SOURCES.md.\nlocal _,A=...\nA.TramData='+lua(result)+'\n',encoding='utf8')
 print('Bundled two native tram directions; no player recordings needed.')
if __name__=='__main__':build()
