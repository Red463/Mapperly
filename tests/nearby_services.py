"""Check the player-relative drawer and its selected-row routing through Lua 5.1."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / '.test-deps'))
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute("A={}")
for module in ('Store', 'TravelNetwork', 'QuestNavigation', 'NearbyServices'):
    lua.execute('assert(loadstring(...))("Mapperly", A)', (root / (module + '.lua')).read_text())
lua.execute("""
local S=A.NearbyServices
A.InitStore({})
A.CrossingData={version=1,maps={
    [1]={name='Player zone',west=1000,north=2000,width=2000,height=4000,instance=0},
    [2]={name='Across the border',west=-1000,north=2000,width=2000,height=4000,instance=0},
    [3]={name='Another world',west=1000,north=2000,width=2000,height=4000,instance=1},
}}
local side='Alliance'
UnitFactionGroup=function()return side end
UnitClass=function()return 'Mage','MAGE',8 end
local position={mapID=1,x=.95,y=.5} -- (-900, 0) world yards
A.Journey={PlayerPosition=function()return position,'Position unavailable.' end}
A.map={GetMapID=function()error('must never use the browsed map')end}
A.ServiceDirectory={[0]={
    {id=1,category='vendor',name='Bowyer',specialty='Bows',repairs=true,x=40,y=-870,access='AH'},
    {id=2,category='trainer',name='Ice',specialty='Mage Trainer',trainerClass=8,x=0,y=-1050,access='A'},
    {id=3,category='trainer',name='Sword',trainerClass=1,x=20,y=-900,access='A'},
    {id=4,category='vendor',name='Horde only',x=0,y=-900,access='H'},
    {id=5,category='vendor',name='Far',x=1700,y=900,access='AH'},
},[1]={{id=6,category='vendor',name='Other continent',x=0,y=-900,access='AH'}}}
A.BundledServices={{id=42,category='inn',name='Innkeeper Faith',instance=0,x=10,y=-900,access='A'}}
A.FlightData={nodes={
    [4]={name='Test town',factionMask=1,world={worldX=-900,worldY=-80,instance=0},
        a={mapID=1,x=.95,y=.519},destinationAvailable=true,approachVerified=true},
    [5]={name='Horde air',factionMask=2,world={worldX=-900,worldY=-15,instance=0},a={mapID=1,x=.95,y=.502}}
}}
local rows,zone,reason=S.List()
assert(zone=='Player zone' and not reason and #rows==4)
assert(rows[1].name=='Innkeeper Faith')
assert(rows[2].name=='Bowyer' and rows[2].distance==50 and rows[2].detail:find('Bows'))
assert(rows[3].category=='flight' and rows[4].distance==150 and rows[4].map==2)
assert(S.List()==rows,'stationary refresh should reuse its sorted result')
local vendor=rows[2]
assert(vendor.npcID==1 and rows[4].npcID==2,'service records must identify the vendor or trainer independently of the spawn location')
local byRole = S.ListByRole()
assert(byRole.vendor[1]==vendor and S.ListByRole()==byRole and #byRole.mail==0)
assert(#S.List('vendor')==1)
assert(#byRole.repair==1 and byRole.repair[1]==vendor,'repairers keep their exact vendor destination')
assert(#S.List('trainer')==1 and S.List('trainer')[1].name=='Ice')
A.db.observed[1]={category='inn',name='Innkeeper Faith',map=1,x=.951,y=.497,access='A'}
A.db.observed[2]={category='mail',name='Mailbox',map=1,x=.95,y=.5,access='A'}
assert(#S.List()==5 and S.List()[1].name=='Mailbox')
position.x=.8
assert(S.List('vendor')[1].distance>200,'moved player updates distances')
assert(S.ListByRole()~=byRole)
A.Terrain={Zone=function()return {}end, Segment=function()return false end,
    Approach=function(p,r)assert(r==30);return {mapID=p.mapID,x=p.x+.001,y=p.y}end}
local last
A.Navigation={Start=function(map,x,y,name)last={map,x,y,name};return true end}
A.db.navigationMode='direct'
assert(S.Navigate(vendor) and last[1]==vendor.map and last[2]==vendor.x*100 and last[4]=='Bowyer')
A.db.navigationMode='terrain'
assert(S.Navigate(vendor) and last[2]==(vendor.x+.001)*100 and last[4]:find('approach'))
local flight=S.List('flight')[1];assert(S.Navigate(flight) and math.abs(last[3]-51.9)<1e-6)
last=nil;position={mapID=3,x=.5,y=.5}
assert(not S.Navigate(vendor) and not last,'stale rows must not navigate after a world change')
side='Horde';position={mapID=1,x=.95,y=.5}
assert(#S.List('trainer')==0 and #S.List('vendor')==2)
position=nil
local empty,_,why=S.List()
assert(#empty==0 and type(why)=='string')

-- An NPC can sell things and keep an inn. The All list shows one
-- destination; filters retain each individual role and action.
side='Alliance';position={mapID=1,x=.95,y=.5}
table.insert(A.ServiceDirectory[0],{id=42,name='Innkeeper Faith',category='vendor',specialty='Innkeeper',access='A',x=10,y=-900})
A.CrossingData.maps[4]={name='Overlap',west=1000,north=2000,width=2000,height=4000,instance=0}
C_Map={GetMapInfo=function(id)
    if id==9 then return {name='Continent',mapType=2} end
    return {name='Zone',mapType=3,parentMapID=9}
end,GetMapInfoAtPosition=function(map)
    return {mapID=map==9 and 4 or map}
end}
LibStub=function()return {GetZoneCoordinatesFromWorldInstance=function()return .5,.5 end}end
local both=S.List()
local combined=0
for _,r in ipairs(both)do
    if r.name=='Innkeeper Faith' then
        assert(r.map==4 and r.detail:find('Vendor'));combined=combined+1
    end
end
assert(combined==1)
assert(#S.List('vendor')==2 and #S.List('inn')==1)
""")
print('PASS: player-relative yardage, filtering, source deduplication, cache refresh and routing')

# Use the actual shipped positions, walking masks, door/city handling and
# planning jobs. Only the client's player-position and map API is simulated.
sys.path.insert(0, str(root / 'tools'))
from benchmark_route_matrix import runtime

game = runtime(profile='firm')
for module in ('Data/Services', 'Data/ServiceDirectory', 'Data/VendorGoods', 'QuestNavigation',
               'NearbyServices', 'NearbyServiceGroups', 'Navigation'):
    game.execute('assert(loadstring(...))("Mapperly", A)', (root / (module + '.lua')).read_text(encoding='utf-8'))
game.execute("""
local start
UnitClass=function()return 'Mage','MAGE',8 end
C_Map={
    GetBestMapForUnit=function()return start.mapID end,
    GetPlayerMapPosition=function()return {GetXY=function()return start.x,start.y end} end,
    GetMapInfo=function(map)return {name=A.CrossingData.maps[map].name} end,
}
LibStub=function()return {
    GetWorldCoordinatesFromZone=function(_,x,y,map)return A.TravelNetwork.World({mapID=map,x=x,y=y})end,
    GetPlayerWorldPosition=function()return A.TravelNetwork.World(start)end,
}end
GetPlayerFacing=function()return 0 end
local function verify(map,x,y,faction,name,kind)
    start={mapID=map,x=x,y=y}
    benchSide=faction
    local rows,zone=A.NearbyServices.List(kind)
    local service
    for _,row in ipairs(rows)do if row.name==name then service=row;break end end
    assert(service and service.map==map,'Wrong map for '..name..' in '..zone)
    assert(service.distance>15 and service.distance<500,'Unexpected distance to '..name)
    local accepted,why=A.NearbyServices.Navigate(service)
    assert(accepted,why)
    while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
    local target=A.Navigation.target
    assert(A.Journey.active and target and target.name:find(name,1,true),A.Navigation.planningError or 'Missing active service destination')
    assert(target.map==map)
    print(string.format('PASS: %s -> %s (%.0f yd direct, %.0f yd walking)',zone,name,service.distance,A.Journey.active.distance))
end
verify(1431,.77,.44,'Alliance','Innkeeper Trelayne','inn')
verify(1429,.423,.666,'Alliance','Zaldimar Wefhellt','trainer')
verify(1429,.423,.666,'Alliance','Corina Steele','repair')
verify(1453,.624,.720,'Alliance','Elaine Trias','vendor')
verify(1413,.509,.305,'Horde','Innkeeper Boorand Plainswind','inn')

-- The reference town contains two different merchants whose actual stock identifies them.
-- Follow a search result through to the real planner in each case.
start = {mapID=1439,x=.365,y=.456}
benchSide='Alliance'
local function shopFor(item, merchant)
    local groups = A.NearbyServiceGroups.List(item)
    for _,group in ipairs(groups) do
        if group.key=='vendor' then
            for _,category in ipairs(group.categories) do
                local previous=-1
                for _,provider in ipairs(category.providers) do
                    local s = provider.service
                    assert(s.distance>=previous)
                    previous=s.distance
                    if s.name==merchant and provider.example==item then
                        assert(s.map==1439 and s.distance>0 and s.distance<2000 and provider.icon)
                        local ok,reason=A.NearbyServices.Navigate(s)
                        assert(ok,reason)
                        while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
                        local target=A.Navigation.target
                        assert(target and target.map==1439 and target.name:find(merchant,1,true))
                        assert(A.Journey.active and #A.Journey.active.legs>0)
                        print(string.format('PASS: Auberdine item search and route: %s -> %s (%.0f yd)',item,merchant,s.distance))
                        return
                    end
                end
            end
        end
    end
    error(item..' missing from '..merchant)
end
shopFor('Sharp Arrow','Dalmond')
shopFor('Moist Cornbread','Kyndri')
local repairGroups=A.NearbyServiceGroups.List('gear repairs')
assert(#repairGroups==1 and repairGroups[1].key=='repair' and #repairGroups[1].categories>0)
local last=0
for _,row in ipairs(repairGroups[1].categories) do
    local s=row.providers[1].service
    assert(s.distance>=last and s.name==row.label and row.icon:find('Hammer'))
    last=s.distance
end
""")
