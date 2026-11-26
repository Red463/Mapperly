"""Small adversarial maps exercise the production accelerated terrain search.

Run with: python tests/terrain_acceleration_quality.py
No native snapshot, matrix replay, or timing threshold is needed.
"""
from pathlib import Path
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
sys.path.insert(0, str(ROOT / 'tools'))
from lupa.lua51 import LuaRuntime
from build_walking_portals import build as build_portals


def packed(cells, width, height):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    return [''.join(alphabet[sum(1 << (5 - bit) for bit in range(6)
                                if x + bit < width and (x + bit, y) in cells)]
                    for x in range(0, width, 6)) for y in range(height)]


class Map:
    def __init__(self, width=144, height=96, roads=None):
        self.width, self.height = width, height
        self.full = {(x, y) for y in range(height) for x in range(width)}
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('A={}')
        for name in ('Terrain.lua', 'Roads.lua', 'Water.lua', 'TerrainPortals.lua', 'PathReuse.lua'):
            self.lua.execute('assert(loadstring(...))("Mapperly",A)',
                             (ROOT / name).read_text())
        self.addon = self.lua.globals().A
        shape = dict(w=width, h=height, widthYards=width * 10,
                     heightYards=height * 10)
        self.shape = shape
        road_cells = roads or set()
        sources = dict(
            TerrainData=dict(version=1, zones={1: dict(shape, status='complete',
                maskSha256='fixture-ground', rows=packed(self.full, width, height))}),
            RoadData=dict(version=1, zones={1: dict(shape, roadCells=len(road_cells),
                rows=packed(road_cells, width, height))}),
            WaterData=dict(version=1, zones={1: dict(w=width, h=height,
                baseSha256='fixture-ground', rows=packed(self.full, width, height))}),
        )
        for key, value in sources.items():
            self.addon[key] = self.lua.table_from(value, recursive=True)
        # Build valid open-map portals first. Tests intentionally retain them
        # while changing the authoritative cells underneath the same hash.
        self.addon.WalkingPortalData = self.lua.table_from(build_portals(self.lua), recursive=True)

    def terrain(self, cells):
        self.addon.TerrainData.zones[1].rows = self.lua.table_from(
            packed(cells, self.width, self.height))
        self.addon.Terrain.ClearPathCache()

    def dry(self, cells):
        self.addon.WaterData.zones[1].rows = self.lua.table_from(
            packed(cells, self.width, self.height))
        self.addon.Terrain.ClearPathCache()

    def point(self, x, y):
        return self.lua.table_from(dict(mapID=1, x=(x + .5) / self.width,
                                       y=(y + .5) / self.height))

    def path(self, start, goal, **options):
        options.setdefault('maxExpansions', 131072)
        return self.addon.Terrain.Path(self.point(*start), self.point(*goal),
                                      self.lua.table_from(options))


class AccelerationQuality(unittest.TestCase):
    def assert_valid(self, fixture, points, **options):
        result = fixture.addon.Terrain.Validate(
            fixture.lua.table_from(dict(points=points)),
            fixture.lua.table_from(options))
        self.assertTrue(result[0] if isinstance(result, tuple) else result)

    def test_stale_optimistic_links_cannot_cross_a_complete_wall(self):
        fixture = Map()
        fixture.terrain(fixture.full - {(72, y) for y in range(fixture.height)})
        path, reason = fixture.path((6, 42), (138, 42))
        self.assertIsNone(path, 'A stale guide authorized a fine-grid wall')
        self.assertIn(reason, ('unreachable', 'budget'))

    def test_stale_links_cannot_squeeze_through_a_blocked_corner(self):
        fixture = Map()
        wall = {(72, y) for y in range(fixture.height) if y != 48}
        fixture.terrain(fixture.full - wall - {(71, 48)})
        self.assertFalse(fixture.addon.Terrain.Segment(
            fixture.point(71, 47), fixture.point(72, 48)))
        path, reason = fixture.path((6, 42), (138, 42))
        self.assertIsNone(path, 'The open diagonal has blocked touching side cells')
        self.assertIn(reason, ('unreachable', 'budget'))

    def test_narrow_detour_outside_the_proposed_corridor_still_routes(self):
        fixture = Map(height=168)
        # The single-cell opening is over ten guide tiles away from the
        # optimistic horizontal proposal, beyond either widening radius.
        wall = {(72, y) for y in range(fixture.height) if y != 150}
        fixture.terrain(fixture.full - wall)
        points, reason = fixture.path((6, 6), (138, 6))
        self.assertIsNotNone(points, reason)
        self.assert_valid(fixture, points)
        self.assertGreater(max(p.y * fixture.height for _, p in points.items()), 150)

    def test_compiled_portals_follow_a_one_cell_channel_with_two_bends(self):
        fixture = Map()
        channel = {(x, 6) for x in range(6, 71)}
        channel.update((70, y) for y in range(6, 79))
        channel.update((x, 78) for x in range(70, 139))
        fixture.terrain(channel)
        fixture.addon.WalkingPortalData = fixture.lua.table_from(
            build_portals(fixture.lua), recursive=True)
        self.assertFalse(fixture.addon.Terrain.Segment(
            fixture.point(6, 6), fixture.point(138, 78)))
        points, reason = fixture.path((6, 6), (138, 78))
        self.assertIsNotNone(points, reason)
        self.assert_valid(fixture, points)
        # Every cell center is on the compiled narrow channel; a coarse chord
        # through either bend would include prohibited terrain.
        for _, p in points.items():
            self.assertIn((math.floor(p.x * fixture.width),
                           math.floor(p.y * fixture.height)), channel)

    def test_stale_dry_links_do_not_authorize_wet_or_unknown_cells(self):
        for unknown in (False, True):
            with self.subTest(unknown=unknown):
                fixture = Map()
                if unknown:
                    # Unknown packed bytes prohibit a six-cell vertical band.
                    rows = packed(fixture.full, fixture.width, fixture.height)
                    rows = [row[:12] + '?' + row[13:] for row in rows]
                    fixture.addon.WaterData.zones[1].rows = fixture.lua.table_from(rows)
                else:
                    fixture.dry(fixture.full - {(72, y) for y in range(fixture.height)})
                points, reason = fixture.path((6, 42), (138, 42), allowSwimming=False)
                self.assertIsNone(points, 'Optimistic dry links overrode native liquid policy')
                self.assertIn(reason, ('unreachable', 'budget'))
                permitted, reason = fixture.path((6, 42), (138, 42), allowSwimming=True)
                self.assertIsNotNone(permitted, reason)
                self.assert_valid(fixture, permitted, allowSwimming=True)
                result = fixture.addon.Terrain.Validate(
                    fixture.lua.table_from(dict(points=permitted)),
                    fixture.lua.table_from(dict(allowSwimming=False)))
                self.assertFalse(result[0] if isinstance(result, tuple) else result)

    def test_missing_dry_provenance_is_not_replaced_by_the_guide(self):
        fixture = Map()
        fixture.addon.WaterData.zones[1].baseSha256 = 'stale-water-source'
        points, reason = fixture.path((6, 42), (138, 42), allowSwimming=False)
        self.assertIsNone(points)
        self.assertEqual(reason, 'blocked endpoint')

    def test_one_cell_road_bend_survives_refinement_and_smoothing(self):
        roads = {(x, 30) for x in range(6, 139)}
        roads.update((x, y) for x in (6, 138) for y in range(30, 49))
        fixture = Map(roads=roads)
        ordinary, direct = fixture.path((6, 48), (138, 48), preferRoads=False)
        self.assertEqual(len(ordinary), 2)
        self.assertAlmostEqual(direct, 1320)
        preferred, distance = fixture.path((6, 48), (138, 48),
                                          preferRoads=True, roadPreferenceStrength=5)
        self.assertIsNotNone(preferred, distance)
        self.assert_valid(fixture, preferred)
        self.assertGreater(distance, direct)
        self.assertLess(distance, direct * 1.35, 'Road preference caused an excessive detour')
        self.assertLess(min(p.y * fixture.height for _, p in preferred.items()), 31)
        from compare_route_road_coverage import sampled_road_coverage
        plain = sampled_road_coverage(fixture.lua, dict(points=ordinary), sample_yards=1)
        road = sampled_road_coverage(fixture.lua, dict(points=preferred), sample_yards=1)
        self.assertGreater(road['roadFraction'], .85, 'A thin road bend was lost')
        self.assertGreater(road['roadFraction'], plain['roadFraction'] + .7)
        repeated, repeat_length = fixture.path((6, 48), (138, 48), preferRoads=False)
        self.assertEqual(len(repeated), 2)
        self.assertAlmostEqual(repeat_length, direct, msg='Road policies shared cached geometry')

    def test_missing_portal_data_preserves_the_exact_road_fallback(self):
        roads = {(x, 30) for x in range(6, 139)}
        roads.update((x, y) for x in (6, 138) for y in range(30, 49))
        fixture = Map(roads=roads)
        # Missing generated component data must retain exact terrain search.
        fixture.addon.WalkingPortalData = None
        preferred, distance = fixture.path((6, 48), (138, 48),
                                          preferRoads=True, roadPreferenceStrength=5)
        self.assertIsNotNone(preferred, distance)
        self.assert_valid(fixture, preferred)
        from compare_route_road_coverage import sampled_road_coverage
        measured = sampled_road_coverage(fixture.lua, dict(points=preferred), sample_yards=1)
        self.assertGreater(measured['roadFraction'], .85, 'Missing portals bypassed exact fallback')

    def test_road_sampler_measures_distance_and_excludes_vehicle_legs(self):
        from compare_route_road_coverage import sampled_road_coverage
        fixture = Map(roads={(x, y) for x in range(72) for y in range(96)})
        start = dict(mapID=1, x=0, y=.5)
        goal = dict(mapID=1, x=1, y=.5)
        route = dict(legs=[dict(kind='walk', points=[start, goal]),
                          dict(kind='boat', points=[start, goal])])
        measured = sampled_road_coverage(fixture.lua, route, sample_yards=10)
        self.assertAlmostEqual(measured['walkingYards'], 1440)
        self.assertAlmostEqual(measured['roadYards'], 720)
        self.assertAlmostEqual(measured['roadFraction'], .5)
        self.assertEqual(measured['samples'], 144)
        self.assertEqual(measured['skippedNonWalkingLegs'], 1)
        fixture.addon.RoadData.zones[1].w = 145
        unknown = sampled_road_coverage(fixture.lua, route, sample_yards=10)
        self.assertEqual(unknown['roadYards'], 0)
        self.assertEqual(unknown['knownRoadYards'], 0)
        self.assertEqual(unknown['unknownRoadYards'], 1440)
        fixture.addon.RoadData.zones[1].w = 144
        fixture.addon.RoadData.zones[1].roadCells = 0
        fixture.addon.RoadData.zones[1].rows = fixture.lua.table_from(
            packed(set(), fixture.width, fixture.height))
        empty = sampled_road_coverage(fixture.lua, route, sample_yards=10)
        self.assertEqual(empty['roadFraction'], 0)
        self.assertEqual(empty['knownRoadYards'], 1440)
        self.assertEqual(empty['unknownRoadYards'], 0)
        for value in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                sampled_road_coverage(fixture.lua, route, sample_yards=value)


if __name__ == '__main__':
    unittest.main()
