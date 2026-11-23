"""Affirmative taxi-window evidence, stable IDs, fares and character isolation."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Flights.lua']:
 if (root/f).exists():lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
assert(A.Flights,'character flight discovery adapter must exist')
A.InitStore({})
A.FlightData={version=1,build=42,nodes={},segments={}}
for _,id in ipairs({2,4,5,8}) do A.FlightData.nodes[id]={id=id,factionMask=1,name='Node '..id} end
local guid='Player-A';local side='Alliance'
UnitGUID=function() return guid end;UnitFactionGroup=function() return side end;UnitClass=function() return 'Mage','MAGE' end
GetTaxiMapID=function() return 146 end
local calls=0;local phase=1
C_TaxiMap={GetAllTaxiNodes=function()
 calls=calls+1
 return {{nodeID=4,slotIndex=7,state=phase==3 and 2 or 1},{nodeID=2,slotIndex=3,state=0},
  {nodeID=5,slotIndex=11,state=phase==2 and 1 or 2},{nodeID=99,slotIndex=12,state=10},
  {nodeID=8,slotIndex=21,state=1,isMapLayerTransition=true}}
end}
TaxiNodeCost=function(slot) assert(slot==7 or slot==11);return slot==7 and 90 or 0 end
GetNumRoutes=function(slot) return slot==7 and 2 or 1 end
TaxiGetNodeSlot=function(slot,i,source)
 if slot==7 then if i==1 then return source and 3 or 11 else return source and 11 or 7 end end
 return source and 3 or 11
end
TakeTaxiNode=function() error('discovery must never purchase or select a flight') end
local F=A.Flights
assert(F.Opened())
local c=assert(F.Character());assert(c.nodes[2] and c.nodes[4])
assert(not c.nodes[5] and not c.nodes[99] and not c.nodes[8],'unreachable, unknown and layer rows cannot unlock destinations')
local offer=assert(c.offers[2][4]);assert(offer.fare==90 and #offer.hops==3 and offer.hops[2]==5,'whole fare and actual hop IDs must survive nonsequential slots')
assert(not c.offers[4],'reverse offering cannot be invented')
F.Closed();local previous=calls;assert(not F.Collect() and calls==previous,'closed taxi window cannot be read')
guid='Player-B';assert(not F.Character().nodes[2],'another character cannot inherit flight discovery')
assert(F.Opened());local b=F.Character();assert(b~=c and b.nodes[4])
F.Closed();guid='Player-A';assert(F.Character()==c)
guid=nil;assert(not F.Opened() and not F.Character(),'missing GUID must fail closed')
assert(not A.db.flightKnowledge['nil'] and not A.db.flightKnowledge['anonymous'])
guid='Player-A';phase=2;assert(F.Opened());assert(c.nodes[5] and c.offers[2][5].fare==0,'free observed itineraries are valid')
phase=3;assert(F.Collect());assert(c.nodes[4] and not c.offers[2][4],'unreachable preserves historical discovery but removes the current source offering')
F.Closed();side='Horde';assert(next(F.Character().offers)==nil,'faction changes invalidate offered routes')
side='Alliance';F.Character()
local old=C_TaxiMap.GetAllTaxiNodes;C_TaxiMap.GetAllTaxiNodes=function() error('protected') end
assert(not F.Opened());F.Closed();previous=calls
F.driver:GetScript('OnUpdate')(F.driver,.1);assert(calls==previous,'closed retry must not collect stale interaction data')
C_TaxiMap.GetAllTaxiNodes=old
phase=1;c=F.Character();c.offers[2]={[4]=true}
assert(F.Opened() and type(c.offers[2][4])=='table','malformed historical offer must be replaced without breaking discovery')
F.Closed();local waiting=true
C_TaxiMap.GetAllTaxiNodes=function(...) if waiting then waiting=false;return {} end;return old(...) end
assert(not F.Opened());F.driver:GetScript('OnUpdate')(F.driver,.1)
assert(F.source==2 and c.offers[2][4],'next-frame retry may collect a newly ready open window')
GetNumRoutes=function() return 3 end
TaxiGetNodeSlot=function(slot,i,source)
 if i==1 then return source and 3 or 11 end
 if i==2 then return source and 11 or 3 end
 return source and 3 or 7
end
assert(F.Collect() and not c.offers[2][4].hops,'cyclic hop metadata must omit geometry, while retaining affirmative offered destination')
F.Closed()
''')
print('PASS: stable discovery IDs, directed offered fares, unknown/protected data and character isolation')
