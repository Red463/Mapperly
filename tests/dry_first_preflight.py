"""Best-effort dry planning stays bounded without weakening explicit policy."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime


def packed(cells, width, height):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    return [''.join(alphabet[sum(1 << (5 - bit) for bit in range(6)
                                if x + bit < width and (x + bit, y) in cells)]
                    for x in range(0, width, 6)) for y in range(height)]


class Fixture:
    def __init__(self, map_id=1, width=48, height=24):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((ROOT / 'tests/wow.lua').read_text())
        self.lua.execute('fakeUI();A={}')
        for name in ('Store.lua', 'Water.lua', 'Terrain.lua', 'PathReuse.lua',
                     'Structures.lua', 'PlanningJob.lua', 'TravelNetwork.lua',
                     'CityNavigation.lua', 'Trams.lua', 'Journey.lua', 'JourneyView.lua'):
            self.lua.execute('assert(loadstring(...))("Mapperly",A)',
                             (ROOT / name).read_text())
        self.addon = self.lua.globals().A
        self.addon.InitStore(self.lua.table_from(dict(avoidSwimming=True)))
        self.map_id, self.width, self.height = map_id, width, height
        self.full = {(x, y) for y in range(height) for x in range(width)}
        shape = dict(w=width, h=height, widthYards=width * 10,
                     heightYards=height * 10)
        self.addon.TerrainData = self.lua.table_from(dict(version=1, zones={map_id:
            dict(shape, status='complete', maskSha256='dry-fixture',
                 rows=packed(self.full, width, height))}), recursive=True)
        self.addon.WaterData = self.lua.table_from(dict(version=1, zones={map_id:
            dict(w=width, h=height, baseSha256='dry-fixture',
                 rows=packed(self.full, width, height))}), recursive=True)
        self.lua.execute('''
            pathCalls={};networkCalls={}
            local path=A.Terrain.Path
            A.Terrain.Path=function(a,b,o)
                pathCalls[#pathCalls+1]={allowed=A.Water.AllowSwimming(),
                                        budget=o and o.maxExpansions}
                return path(a,b,o)
            end
            local network=A.TravelNetwork.Plan
            A.TravelNetwork.Plan=function(a,b,o)
                networkCalls[#networkCalls+1]={allowed=A.Water.AllowSwimming(),
                                              budget=o and o.maxWalkingCells}
                return network(a,b,o)
            end
        ''')

    def dry(self, cells):
        self.addon.WaterData.zones[self.map_id].rows = self.lua.table_from(
            packed(cells, self.width, self.height))

    def point(self, x, y):
        return self.lua.table_from(dict(mapID=self.map_id,
            x=(x + .5) / self.width, y=(y + .5) / self.height))

    def plan(self, start=(6, 12), goal=(42, 12), **options):
        return self.addon.Journey.Plan(self.point(*start), self.point(*goal),
                                       self.lua.table_from(options))


class DryFirstPreflight(unittest.TestCase):
    def test_default_best_effort_budget_does_not_reduce_swimming_retry(self):
        fixture = Fixture()
        fixture.dry(fixture.full - {(24, y) for y in range(24)})
        plan = fixture.plan()
        if isinstance(plan, tuple):
            plan = plan[0]
        self.assertTrue(plan.swimmingFallback)
        calls = fixture.lua.globals().pathCalls
        self.assertFalse(calls[1].allowed)
        self.assertGreaterEqual(calls[1].budget, 64000)
        self.assertLessEqual(calls[1].budget, 150000)
        self.assertTrue(calls[2].allowed)
        self.assertEqual(calls[2].budget, 262144)
        self.assertEqual(plan.swimmingFallbackReason, 'unconfirmed')

    def test_caller_limit_is_preserved_and_budget_fallback_is_disclosed(self):
        fixture = Fixture()
        fixture.dry(fixture.full - {(24, y) for y in range(24)})
        options = fixture.lua.table_from(dict(maxWalkingCells=512, speed=9))
        plan = fixture.addon.Journey.Plan(fixture.point(6, 12), fixture.point(42, 12), options)
        if isinstance(plan, tuple):
            plan = plan[0]
        calls = fixture.lua.globals().pathCalls
        self.assertEqual(calls[1].budget, 512)
        self.assertEqual(calls[2].budget, 512)
        self.assertEqual(options.maxWalkingCells, 512)
        self.assertEqual(options.speed, 9)
        self.assertEqual(plan.swimmingFallbackReason, 'budget')
        self.assertEqual(plan.drySearchBudget, 512)

    def test_quick_dry_detour_still_wins_over_shorter_swimming(self):
        fixture = Fixture()
        fixture.dry(fixture.full - {(24, y) for y in range(24) if y != 20})
        plan = fixture.plan()
        if isinstance(plan, tuple):
            plan = plan[0]
        self.assertFalse(plan.swimmingFallback)
        self.assertGreater(plan.distance, 360)
        self.assertEqual(len(fixture.lua.globals().pathCalls), 1)
        result = fixture.addon.Terrain.Validate(plan, fixture.lua.table_from(dict(allowSwimming=False)))
        self.assertIs(result[0] if isinstance(result, tuple) else result, True)

    def test_network_cap_preserves_the_original_caller_retry_allowance(self):
        fixture = Fixture()
        fixture.lua.execute('''
            A.CrossingData={version=1,build=1,maps={},edges={}}
            for _,id in ipairs({1,2})do
                A.CrossingData.maps[id]={name='Map '..id,west=480,north=240,
                    width=480,height=240,instance=0}
            end
            A.TerrainData.zones[2]=A.TerrainData.zones[1]
            A.WaterData.zones[2]=A.WaterData.zones[1]
        ''')
        options = fixture.lua.table_from(dict(maxWalkingCells=900000))
        result = fixture.addon.Journey.Plan(fixture.point(6, 12),
            fixture.lua.table_from(dict(mapID=2,x=.5,y=.5)), options)
        self.assertIsNone(result[0])
        calls = fixture.lua.globals().networkCalls
        self.assertEqual(len(calls), 2)
        self.assertFalse(calls[1].allowed)
        self.assertLessEqual(calls[1].budget, 150000)
        self.assertTrue(calls[2].allowed)
        self.assertEqual(calls[2].budget, 900000)
        self.assertEqual(options.maxWalkingCells, 900000)

    def test_required_dry_and_explicit_swimming_bypass_preference_budget(self):
        for allowed in (False, True):
            with self.subTest(allowed=allowed):
                fixture = Fixture()
                fixture.dry(fixture.full - {(24, y) for y in range(24)})
                result = fixture.plan(allowSwimming=allowed, maxWalkingCells=400000)
                route = result[0] if isinstance(result, tuple) else result
                self.assertEqual(route is not None, allowed)
                calls = fixture.lua.globals().pathCalls
                self.assertEqual(len(calls), 1)
                self.assertEqual(calls[1].allowed, allowed)
                self.assertEqual(calls[1].budget, 262144)

    def test_wet_goal_proof_skips_the_dry_attempt(self):
        fixture = Fixture()
        fixture.dry(fixture.full - {(42, 12)})
        plan = fixture.plan()
        if isinstance(plan, tuple):
            plan = plan[0]
        self.assertTrue(plan.swimmingFallback)
        self.assertEqual(plan.swimmingFallbackReason, 'endpoint')
        calls = fixture.lua.globals().pathCalls
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[1].allowed)

    def test_direct_search_work_is_deducted_before_network_fallback(self):
        fixture = Fixture()
        fixture.dry(fixture.full - {(24, y) for y in range(24)})
        fixture.lua.execute('''
            A.CrossingData={version=1,build=1,maps={[1]={name='Test',
                west=480,north=240,width=480,height=240,instance=0}},edges={}}
            A.StructureData={version=1,build=1,corridors={}}
        ''')
        plan = fixture.plan(maxWalkingCells=512)
        if isinstance(plan, tuple):
            plan = plan[0]
        self.assertTrue(plan.swimmingFallback)
        self.assertEqual(plan.swimmingFallbackReason, 'budget')
        self.assertEqual(fixture.lua.globals().networkCalls[1].budget, 0)

    def test_city_floor_exception_is_not_classified_as_a_wet_endpoint(self):
        fixture = Fixture(map_id=1455)
        fixture.dry(set())
        plan = fixture.plan()
        if isinstance(plan, tuple):
            plan = plan[0]
        self.assertTrue(plan.hasCityGuidance)
        self.assertFalse(plan.swimmingFallback)
        self.assertFalse(fixture.lua.globals().pathCalls[1].allowed)

    def test_certified_native_floor_endpoint_remains_a_dry_route(self):
        fixture = Fixture(width=6, height=3)
        fixture.dry(fixture.full - {(2, 1), (3, 1)})
        fixture.lua.execute('''
            A.CrossingData={version=1,build=1,maps={[1]={name='Bridge test',
                west=60,north=30,width=60,height=30,instance=0}},edges={}}
            local a,b={mapID=1,x=.25,y=.5},{mapID=1,x=.75,y=.5}
            local row={source='native-model-floor',samples=3,maximumStep=0,
                headroom=3,endpointAccess=true,radius=.5,a=a,b=b,distance=30,
                worldPath={{45,15,5},{30,15,5},{15,15,5}}}
            A.StructureData={version=1,build=1,corridors={[10]=row}}
            A.CrossingData.edges={{id=1,a=a,b=b,structure=10,distance=30}}
        ''')
        plan = fixture.addon.Journey.Plan(
            fixture.lua.table_from(dict(mapID=1,x=.5,y=.5)),
            fixture.lua.table_from(dict(mapID=1,x=.75,y=.5)))
        if isinstance(plan, tuple):
            plan = plan[0]
        self.assertIsNotNone(plan)
        self.assertFalse(plan.swimmingFallback)
        self.assertTrue(any(leg.exitStructure == 10 for _, leg in plan.legs.items()))

    def test_issued_flight_boarding_context_survives_wet_root_preflight(self):
        fixture = Fixture()
        fixture.dry(fixture.full - {(6, 12)})
        for name in ('Flights.lua', 'Transports.lua'):
            fixture.lua.execute('assert(loadstring(...))("Mapperly",A)',
                                (ROOT / name).read_text())
        fixture.lua.globals().boardingPoint = fixture.point(6, 12)
        fixture.lua.globals().flightGoal = fixture.point(42, 12)
        fixture.lua.execute('''
            UnitGUID=function()return 'Player-DryBoarding'end
            UnitFactionGroup=function()return 'Alliance'end
            UnitClass=function()return 'Mage','MAGE'end
            UnitOnTaxi=function()return false end
            GetMoney=function()return 1000 end
            A.CrossingData={version=1,build=1,maps={[1]={name='Flight test',
                west=480,north=240,width=480,height=240,instance=0}},edges={}}
            local function node(id,p)
                local x,y,i=A.TravelNetwork.World(p)
                return {id=id,name='Master '..id,factionMask=1,a=p,
                        world={worldX=x,worldY=y,instance=i},z=10}
            end
            A.FlightData={version=1,build=1,nodes={
                [1]=node(1,boardingPoint),[2]=node(2,flightGoal)},segments={}}
            A.FlightData.segments['1:2']={cost=0,seconds=10,path={
                A.FlightData.nodes[1].world,A.FlightData.nodes[2].world}}
            local flights=A.Flights
            local character=flights.Character()
            character.nodes={[1]=true,[2]=true}
            character.offers={[1]={[2]={from=1,to=2,fare=0,hops={1,2}}}}
            flights.open=true;flights.source=1;flights.sessionGUID='Player-DryBoarding'
            boardingContext=assert(flights.BoardingContext(boardingPoint))
            flights.Closed()
            boardedPlan=assert(A.Journey.Plan(boardingPoint,flightGoal,
                {boardingContext=boardingContext,faction='Alliance'}))
        ''')
        plan = fixture.lua.globals().boardedPlan
        self.assertFalse(plan.swimmingFallback)
        self.assertTrue(any(leg.transport and leg.transport.kind == 'flight'
                            for _, leg in plan.legs.items()))
        self.assertFalse(fixture.lua.globals().networkCalls[1].allowed)

    def test_preview_distinguishes_budget_from_unconfirmed_dry_route(self):
        fixture = Fixture()
        fixture.lua.execute('''
            local view=A.JourneyView
            for _,key in ipairs({'summary','warning','steps','skip','pause','resume'})do
                view[key]=CreateFrame('Frame')
            end
            view.plan={kind='walking',name='Test',distance=10,estimatedSeconds=2,
                coverage='complete',swimmingFallback=true,legs={}}
            view.plan.swimmingFallbackReason='budget';view.WriteSummary()
            budgetWarning=view.warning:GetText()
            view.plan.swimmingFallbackReason='unconfirmed';view.WriteSummary()
            genericWarning=view.warning:GetText()
        ''')
        self.assertIn('limit', fixture.lua.globals().budgetWarning)
        self.assertNotIn('No dry route was found', fixture.lua.globals().genericWarning)
        self.assertIn('could not be confirmed', fixture.lua.globals().genericWarning)


if __name__ == '__main__':
    unittest.main()
