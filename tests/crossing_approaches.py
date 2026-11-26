"""The approach audit must prove owned dry ground, not overlapping artwork."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_crossing_approaches import area_owner, audit_side, audit_border_approach, verify_inventory
import hashlib
verify_inventory(b'one',dict(inventorySha256=hashlib.sha256(b'one').hexdigest()))
try:verify_inventory(b'two',dict(inventorySha256=hashlib.sha256(b'one').hexdigest()))
except ValueError:pass
else:raise AssertionError('renumbered/rebuilt inventories must not reuse stale approach evidence')

assert area_owner(3,{1:1455},{3:2,2:1})==1455
assert area_owner(3,{}, {3:2,2:3}) is None

def native(n,e):
    return dict(permitted=True,liquid=False,height=0,area=1)
def point(n,e):return dict(mapID=1,x=.5+n/1000,y=.5+e/1000)
def route(a,b):return True,75
def run(sample=native,owner=lambda a:1,route=route,height=None):
    return audit_side((0,0),1,point,sample,owner,route,floor_height=height)
assert run()['status']=='verified-ground-approach'
assert run(owner=lambda a:2)['status']=='unresolved-approach'
assert run(sample=lambda n,e:dict(native(n,e),liquid=True))['status']=='unresolved-approach'
assert run(route=lambda a,b:(False,'budget'))['status']=='unresolved-approach'
assert run(height=10)['status']=='interior-floor-approach-required'
oneway=run(route=lambda a,b:(a['x']==.5 and a['y']==.5, 'one-way failure'))
assert oneway['status']=='unresolved-approach','both approach directions must pass'
print('PASS: owned dry approaches, bidirectional access, inconclusive budgets and vertical-floor separation')

import json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'tools/data/crossing-approaches-manifest.json').read_text())
assert len(manifest['links'])>=180
assert sum(manifest['counts'].values())==2*len(manifest['links'])
assert manifest['crossingDataSha256']==hashlib.sha256((root/'Data/Crossings.lua').read_bytes()).hexdigest()
assert all(s['status']!='unresolved-approach'for row in manifest['links']for s in row['sides'])
assert manifest['liveStatus']=='not-tested'

algaz = {73025, 126354, 68441769, 68443158}
tunnels = [row for row in manifest['links'] if row['structure'] in algaz]
assert {row['structure'] for row in tunnels} == algaz
assert all(side['status']=='verified-ground-approach' and side['policy']=='dry-only'
           for row in tunnels for side in row['sides']), 'Both Dun Algaz portals need a reachable dry approach'

# The Stranglethorn bridge's north bank has eleven yards of approach before
# the native Duskwood road border. Check the real probe owner and both pieces.
bridge=next(r for r in manifest['links'] if r['structure']==479338901316938)
north=bridge['sides'][0]
assert north['mapID']==1434 and north['point']['mapID']==1431
assert north['status']=='verified-ground-approach-via-zone-crossing' and north['policy']=='dry-only'
via=north['viaCrossing']
road=next(r for r in manifest['links'] if r['id']==via['id'])
assert road['source']=='road-boundary' and road['sides'][0]['point']==north['point']
assert abs(north['distance']-sum(via[k] for k in ('bankWalkYards','crossingYards','approachWalkYards')))<1e-6

def border_probe(segment=lambda *_:True,ground=lambda *_:True,walk=lambda *_:(True,10),far_x=150):
    def p(zone,x):return dict(mapID=zone,x=x,y=0)
    edge=dict(id=1,source='road-boundary',a=p(1,10),b=p(2,30))
    outer=dict(point=p(2,far_x),status='verified-ground-approach',policy='dry-only',world=[far_x,0,0],area=20)
    return audit_border_approach(p(1,0),p(1,-30),[edge],{1:{'sides':[{},outer]}},lambda p:(p['x'],p['y']),segment,ground,walk)
assert border_probe()['point']['mapID']==2
assert not border_probe(segment=lambda zone,a,b:zone==1),'both crossing masks must admit the road connector'
assert not border_probe(ground=lambda a,b,maps:len(maps)==1),'the actual shared native ground is required'
assert not border_probe(walk=lambda a,b:(a['x']<=b['x'],10)),'both approach walking directions must pass'
assert not border_probe(far_x=-100),'the far probe must face away from the other bank'
