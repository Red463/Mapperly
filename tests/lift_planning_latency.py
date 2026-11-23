"""Nearby Great Lift planning must not explore unrelated marsh routes first."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua',
          'Data/Crossings.lua','Data/Structures.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/Flights.lua',
          'Roads.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelNetwork.lua',
          'Flights.lua','Transports.lua','Journey.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
lua.execute('''
A.InitStore({preferRoads=true})
local result,reason;local visits={};local frames=0
A.PlanningJob.Start(function()
 return A.Journey.Plan({mapID=1413,x=.4422,y=.9017},{mapID=1441,x=.2922,y=.3425},{faction='Alliance'})
end,function(plan) result=plan end,function(why) reason=why end)
while A.PlanningJob.IsRunning() and frames<100 do
 A.PlanningJob.Step();frames=frames+1
 local p=A.PlanningJob.Progress();if p and p.mapID then visits[p.mapID]=true end
end
local progress=A.PlanningJob.Progress()
print('Lift planning frames:',frames,'unrelated Dustwallow:',not not visits[1445],'cells:',progress and progress.cells or 'complete')
assert(result,reason or 'nearby lift route did not finish within 100 work slices')
assert(not visits[1445],'nearby verified lift should not search Dustwallow Marsh')
local found=false
for _,leg in ipairs(result.legs) do if leg.transport and leg.transport.kind=='lift' then found=true end end
assert(found,'nearby route must use Great Lift')
''')
print('PASS: full-data nearby lift planning latency and relevant-zone search')
