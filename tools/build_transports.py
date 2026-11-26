"""Build directed scheduled transport links from the pinned native audit."""
from pathlib import Path
import sys,json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'))
from lupa.lua51 import LuaRuntime
from build_harbour_access import build as build_harbour_access

def main():
 source=ROOT/'tools/data/native-transports-70959.json';audit=json.loads(source.read_text(encoding='utf-8-sig'))
 zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
 lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={}')
 for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Terrain.lua']:lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text())
 safe=lua.eval('function(id,x,y) return A.Terrain.Segment({mapID=id,x=x,y=y},{mapID=id,x=x,y=y}) end')
 harbour=build_harbour_access()
 harbour_source=ROOT/'tools/data/native-harbour-corridors-70959.json'
 overrides={}
 for corridor in json.loads(harbour_source.read_text(encoding='utf8')):
  override=corridor.get('endpointOverride')
  if override:
   compiled=harbour['corridors'][override['corridorID']]
   assert compiled['b']=={k:override[k] for k in ('mapID','x','y')}
   assert override['groundHeight']==compiled['worldB'][2] and override['manualBoarding']
   overrides[override['vesselNodeID']]=override
 edges=[];excluded=[]
 def point(stop):
  override=overrides.get(stop['sourceNodeID'])
  if override:
   n,e,z=override['worldPosition'];center=stop['position']
   assert math.hypot(n-center[0],e-center[1])<=25 and safe(override['mapID'],override['x'],override['y'])
   return {k:override[k] for k in ('mapID','x','y')}
  a=stop['approach'];id=a['mapID'];n,e=a['position'];z=zones[id]
  x=(z['west']-e)/(z['west']-z['east']);y=(z['north']-n)/(z['north']-z['south'])
  proof=a.get('groundHeightProof',{})
  if not proof.get('permitted') or proof.get('hole') or proof.get('liquid') or not math.isfinite(a.get('groundHeight',math.nan)):
   raise ValueError('Missing native dry ground/height proof')
  if a['status']!='dry-approach-candidate' or a['distanceToTransportCenterYards']>300 or not safe(id,x,y):raise ValueError('No permitted dry land approach')
  return dict(mapID=id,x=x,y=y)
 def world(node):
  p=node['position'];return dict(worldX=p[1],worldY=p[0],instance=node['continent'])
 for row in audit['links']:
  try:
   a,b=point(row['fromStop']),point(row['toStop'])
   if row['recommendedFaction'] not in ('Neutral','Alliance','Horde'):raise ValueError('Unknown faction routing policy')
   path=[]
   for piece in row['geometryPieces']:
    for i,node in enumerate(piece):
     p=world(node);p['breakBefore']=i==0;path.append(p)
   route=next(r for r in audit['routes'] if r['pathID']==row['pathID'])
   cruise=row.get('nativeCruiseEstimateSeconds');speed=route.get('speedYardsPerSecond');accel=route.get('accelerationYardsPerSecondSquared')
   ride=cruise+(speed/accel if speed and accel else 0) if cruise is not None else 180
   edges.append(dict(id=row['id'],pathID=row['pathID'],kind=row['kind'],name=row['direction'],faction=row['recommendedFaction'],
    a=a,b=b,board=world(row['fromStop']),arrival=world(row['toStop']),arrivalGroundHeight=overrides.get(row['toStop']['sourceNodeID'],row['toStop']['approach']).get('groundHeight'),fromName=row['fromStop']['name'],toName=row['toStop']['name'],
    boardingAccess='dock' if row['fromStop']['sourceNodeID'] in overrides else 'harbour access' if row['fromStop']['approach'].get('verticalManualAccessRequired') else None,
    arrivalAccess='dock' if row['toStop']['sourceNodeID'] in overrides else 'harbour access' if row['toStop']['approach'].get('verticalManualAccessRequired') else None,
    boardingCorridor=overrides.get(row['fromStop']['sourceNodeID'],{}).get('corridorID'),arrivalCorridor=overrides.get(row['toStop']['sourceNodeID'],{}).get('corridorID'),
    fromNodeID=row['fromStop']['sourceNodeID'],toNodeID=row['toStop']['sourceNodeID'],
    planningSeconds=math.ceil(ride+120),rideEstimateSeconds=ride,waitAssumptionSeconds=120,unknownSpeed=cruise is None,
    originDwellSeconds=row['fromStop']['delay'],path=path))
   if row['id']=='transport:241:29:11':
    # Player-observed dock end of the Booty Bay gangplank, rounded by the HUD.
    edges[-1]['boardingPlank']=dict(mapID=1434,x=.260,y=.732)
  except (ValueError,KeyError) as error:excluded.append(dict(id=row['id'],reason=str(error)))
 def literal(v):
  if isinstance(v,dict):return '{'+','.join('['+literal(k)+']='+literal(x) for k,x in v.items())+'}'
  if isinstance(v,list):return '{'+','.join(literal(x) for x in v)+'}'
  if v is True:return 'true'
  if v is False:return 'false'
  if v is None:return 'nil'
  return json.dumps(v)
 data=dict(version=1,build=audit['build'],sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),harbourProofSha256=harbour['proofSha256'],edges=edges)
 (ROOT/'Data/Transports.lua').write_text('-- Native directed transport stops; see Transports-SOURCES.md.\nlocal _,A=...\nA.TransportData='+literal(data)+'\n',encoding='utf8')
 out=ROOT.parent/'output/transport-audit-70959';out.mkdir(exist_ok=True)
 (out/'runtime-inventory.json').write_text(json.dumps(dict(edges=edges,excluded=excluded),indent=2))
 print('Scheduled transports:',len(edges),'directed links;',len(excluded),'unsupported approaches')
 for r in excluded:print(r)

if __name__=='__main__':main()
