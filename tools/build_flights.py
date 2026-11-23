"""Compile pinned native flight geometry; availability is always live character evidence."""
from pathlib import Path
import json, hashlib, math, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'))
from lupa.lua51 import LuaRuntime

def literal(v):
 if isinstance(v,dict): return '{'+','.join('['+literal(k)+']='+literal(x) for k,x in v.items())+'}'
 if isinstance(v,list): return '{'+','.join(literal(x) for x in v)+'}'
 if v is True:return 'true'
 if v is False:return 'false'
 if v is None:return 'nil'
 return json.dumps(v,ensure_ascii=True,allow_nan=False)

def main():
 source=ROOT/'tools/data/native-flights-70959.json'
 audit=json.loads(source.read_text(encoding='utf-8-sig'))
 zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
 lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={}')
 for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/Crossings.lua','Data/WalkingRegions.lua','Terrain.lua','WalkingRegions.lua']:
  lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text(encoding='utf8'))
 safe=lua.eval('function(m,x,y) local p={mapID=m,x=x,y=y};return A.Terrain.Segment(p,p) end')
 nodes={};segments={};unavailable=[]
 for n in audit['nodes']:
  if not n['eligible']:continue
  native=n['position'];approach=n.get('runtimeApproach') or {}
  map_id=approach.get('mapID') or n['mapID'];z=zones[map_id]
  pos=approach.get('position') or native
  north,east=pos[:2]
  x=(z['west']-east)/(z['west']-z['east']);y=(z['north']-north)/(z['north']-z['south'])
  permitted=bool(safe(map_id,x,y)) and approach.get('destinationAvailable',True)
  anchor=approach.get('sourceAnchor',{})
  if anchor.get('kind')=='verified-city-exit':
   edge=lua.globals().A.CrossingData.edges[anchor['crossingIndex']]
   gate=edge.a if edge.a.mapID==map_id else edge.b
   point=lua.table_from(dict(mapID=map_id,x=x,y=y))
   region=lua.globals().A.WalkingRegions.Get
   assert gate.mapID==map_id and region(point)==region(gate) and region(point)>0,'Flight handoff disconnected from verified city exit'
  # A blocked master remains eligible as an observed, already-at-NPC source.
  # It cannot be a destination without a separately verified permitted handoff.
  if not permitted:unavailable.append(n['id'])
  landing=pos[2] if approach.get('heightKind')=='native-ground' else native[2]
  nodes[n['id']]=dict(id=n['id'],name=n['name'],factionMask=n['factionMask'],classToken=n.get('classToken'),
   a=dict(mapID=map_id,x=x,y=y),world=dict(worldX=native[1],worldY=native[0],instance=n['continentID']),
   z=native[2],landingZ=landing,manualAccess=n.get('approach',{}).get('manualAccessRequired',False),
   approachVerified=permitted,destinationAvailable=permitted,approachMethod=approach.get('method','native master XY; native pad height'))
  assert 0<=x<=1 and 0<=y<=1 and math.isfinite(landing)
  assert math.hypot(north-native[0],east-native[1])<=100.001
 for edge in audit['edges']:
  if not edge['eligible']:continue
  a,b=edge['fromNodeID'],edge['toNodeID'];assert a in nodes and b in nodes
  key=f'{a}:{b}';assert key not in segments
  instance=nodes[a]['world']['instance'];assert instance==nodes[b]['world']['instance']
  path=[dict(worldX=p[1],worldY=p[0],instance=instance) for p in edge['polyline']]
  assert len(path)>=2 and 0<edge['estimatedTravelSeconds']<7200 and edge['baseCostCopper']>=0
  segments[key]=dict(sourcePathID=edge['sourcePathID'],seconds=edge['estimatedTravelSeconds'],cost=edge['baseCostCopper'],path=path)
 data=dict(version=1,build=audit['build'],sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),nodes=nodes,segments=segments)
 (ROOT/'Data/Flights.lua').write_text('-- Native flight geometry, never character discovery. See Flights-SOURCES.md.\nlocal _,A=...\nA.FlightData='+literal(data)+'\n',encoding='utf8')
 print(f'Native flights: {len(nodes)} masters, {len(segments)} directed segments; {len(unavailable)} destination handoffs unavailable: {unavailable}')
if __name__=='__main__':main()
