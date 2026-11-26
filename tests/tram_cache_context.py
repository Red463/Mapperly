"""Dock middle caches must keep strict and portal-guidance contexts separate.

Small fixtures use the real Terrain, Structures, Transports, and Trams code.
"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime

def fixture():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow.lua').read_text())
    lua.execute('fakeUI();A={}')
    for name in ('Store.lua', 'Terrain.lua', 'Structures.lua', 'Transports.lua', 'Trams.lua'):
        lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / name).read_text())
    lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / 'TravelNetwork.lua').read_text())
    lua.execute('''
        A.InitStore({})
        A.TerrainData={version=1,zones={}}
        A.CrossingData={version=1,build=1,maps={},edges={}}
        for _,map in ipairs({1453,2,3})do
            A.TerrainData.zones[map]={status='complete',w=12,h=6,
                widthYards=100,heightYards=100,
                rows={'/f','/f','/f','/f','/f','/f'}}
            A.CrossingData.maps[map]={name='Zone '..map,west=100,north=100,
                width=100,height=100,instance=map==3 and 1 or 0}
        end
        A.TerrainData.zones[3].rows={'//','//','//','//','//','//'}
        function point(map,col) return {mapID=map,x=(col+.5)/12,y=2.5/6} end
        function world(p)
            local x,y,i=A.TravelNetwork.World(p)
            return {worldX=x,worldY=y,instance=i}
        end
        start=point(1453,1);ground=point(1453,8);dock=point(1453,10)
        other=point(2,1);distantDock=point(2,10);goal=point(3,6)
        local first,last=world(ground),world(dock)
        local distance=A.TravelNetwork.Distance(ground,dock)
        local floor={a=ground,b=dock,source='native-wmo-floor',samples=3,
            maximumStep=0,headroom=5,distance=distance,
            worldPath={{first.worldX,first.worldY,5},
                       {(first.worldX+last.worldX)/2,first.worldY,5},
                       {last.worldX,last.worldY,5}}}
        A.StructureData={version=1,build=1,corridors={[10]=floor}}
        A.HarbourAccessData={version=1,build=1,proofSha256='fixture-proof',corridors={[10]=floor}}
        function service(id,kind,a,b,seconds)
            return {id=id,kind=kind,name=id,faction='Alliance',a=a,b=b,
                board=world(a),arrival=world(b),planningSeconds=seconds,
                fromName='Source',toName='Destination'}
        end
        local tram=service('one-way-tram','tram',point(1453,8),other,1)
        tram.automaticTram=true;tram.faction='Neutral'
        A.TramData={version=1,build=1,edges={tram}}
        local direct=service('strict-boat','boat',dock,goal,200)
        direct.boardingCorridor=10
        local onward=service('blocked-onward','boat',distantDock,goal,1)
        A.TransportData={version=1,build=1,harbourProofSha256='fixture-proof',edges={direct,onward}}
        portalCalls=0
        local access=A.Trams.Access
        A.Trams.Access=function(...)
            local points,length=access(...)
            if points then portalCalls=portalCalls+1 end
            return points,length
        end
        function plan(a,b,side)
            return A.TravelNetwork.Plan(a,b,{speed=1,faction=side or 'Alliance',maxWalkingCells=10000})
        end
    ''')
    return lua


class TramContext(unittest.TestCase):
    def test_portal_success_cannot_authorize_a_strict_dock_middle(self):
        lua = fixture()
        lua.execute('result,why=plan(start,goal)')
        self.assertGreater(lua.globals().portalCalls, 0, 'Fixture must first validate the one-way tram approach')
        self.assertIsNone(lua.globals().result,
                          'Portal-bearing cache entry fabricated a walking chord across the dock-access wall')

    def test_strict_failure_cannot_poison_a_later_tram_portal_approach(self):
        lua = fixture()
        lua.execute('''
            A.TramData.edges[1].planningSeconds=100
            A.TransportData.edges[1].planningSeconds=1
            A.TransportData.edges[2]=service('sea-return','boat',goal,other,1)
            result,why=plan(start,other)
        ''')
        route = lua.globals().result
        self.assertIsNotNone(route, lua.globals().why)
        rides = [leg.transport.id for _, leg in route.legs.items() if leg.transport]
        self.assertEqual(rides, ['one-way-tram'])

    def test_one_way_tram_remains_one_way(self):
        lua = fixture()
        lua.execute('forward=assert(plan(start,other));backward=plan(other,start)')
        self.assertTrue(lua.globals().forward.hasTransports)
        self.assertIsNone(lua.globals().backward, 'A virtual station invented the missing reverse tram')

    def test_faction_and_disabled_tram_do_not_create_alternate_city_walks(self):
        lua = fixture()
        lua.execute('''
            friendly=assert(plan(ground,goal,'Alliance'))
            hostile=plan(ground,goal,'Horde')
            A.db.useTrams=false
            noVirtualStation=plan(start,goal,'Alliance')
        ''')
        self.assertTrue(lua.globals().friendly.hasTransports)
        self.assertIsNone(lua.globals().hostile)
        self.assertIsNone(lua.globals().noVirtualStation)

    def test_valid_strict_middle_retains_the_entire_native_pier(self):
        lua = fixture()
        lua.execute('''
            result=assert(plan(point(1453,7),goal))
            local row=A.HarbourAccessData.corridors[10]
            for _,native in ipairs(row.worldPath)do
                local found=false
                for _,p in ipairs(result.points)do
                    local x,y=A.TravelNetwork.World(p)
                    if x and (x-native[1])^2+(y-native[2])^2<1e-10 then found=true end
                end
                assert(found,'Dock composition omitted a certified native pier point')
            end
            for _,leg in ipairs(result.legs)do
                if leg.kind=='walk' then
                    assert(not leg.portalGuidance,'A verified dock approach must use its actual middle and floor')
                    assert(A.Terrain.Validate(leg))
                end
            end
        ''')
        self.assertIsNotNone(lua.globals().result)


if __name__ == '__main__':
    unittest.main()
