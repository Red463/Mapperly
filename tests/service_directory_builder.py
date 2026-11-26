"""Snapshot selection and coverage regressions for the nearby services drawer."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_service_directory as directory


def fixture():
    return [
        ('creature_template', dict(entry='77', name='Example', subname='Rogue Trainer',
                                   npcflag=str(0x20 | 0x100 | 0x1000), trainer_class='4', faction='12')),
        ('creature', dict(guid='14', id='77', map='0', position_x='-55.25', position_y='12.5')),
    ]


FACTIONS = {12: dict(FactionGroup=2, FriendGroup=2, EnemyGroup=4)}


class ServiceDirectoryTests(unittest.TestCase):
    def test_distinct_capabilities_world_axes_and_faction(self):
        rows = fixture()
        rows.append(('creature', dict(rows[-1][1], guid='15')))
        trainer, vendor = directory.extract(rows, FACTIONS)[0]
        self.assertEqual(trainer, dict(category='trainer', id=77, name='Example', x=-55.25, y=12.5,
                                       access='A', specialty='Rogue Trainer', trainerClass=4))
        self.assertTrue(vendor['repairs'])
        self.assertNotIn('trainerClass', vendor)

    def test_spawn_can_add_or_remove_capabilities(self):
        rows = fixture()
        rows[1][1]['npcflag'] = '0'
        self.assertEqual(directory.extract(rows, FACTIONS), {})
        rows[0][1]['npcflag'] = '0'
        rows[1][1]['npcflag'] = '128'
        self.assertEqual([r['category'] for r in directory.extract(rows, FACTIONS)[0]], ['vendor'])
        rows[1][1]['npcflag'] = str(directory.REPAIR)
        self.assertEqual([r['category'] for r in directory.extract(rows, FACTIONS)[0]], ['repair'])

    def test_unsupported_and_conditional_spawns_are_excluded(self):
        for field, value in [('map', '33'), ('PhaseId', '6'), ('terrainSwapMap', '0'),
                             ('position_x', 'nan'), ('spawnDifficulties', '0,1')]:
            rows = fixture()
            rows[1][1][field] = value
            self.assertEqual(directory.extract(rows, FACTIONS), {}, field)
        for extra in [[('pool_members', dict(type='0', spawnId='14'))],
                      [('game_event_creature', dict(guid='14'))],
                      [('conditions', dict(SourceTypeOrReferenceId='32', SourceEntry='77'))],
                      [('spawn_group_template', dict(groupId='3', groupFlags='4')),
                       ('spawn_group', dict(groupId='3', spawnType='0', spawnId='14'))]]:
            self.assertEqual(directory.extract(fixture() + extra, FACTIONS), {}, extra)
        self.assertEqual(directory.extract(fixture(), {}), {})

    def test_shipped_snapshot_has_known_services_on_both_continents(self):
        catalog = (ROOT / 'Data/ServiceDirectory.lua').read_text(encoding='utf-8')
        for record in ['category="vendor",id=1285,name="Thurman Mullby",x=-8831.75,y=596.355,access="A"',
                       'category="vendor",id=3322,name="Kaja",x=1692.69,y=-4412.03,access="H"',
                       'category="trainer",id=917,name="Keryn Sylvius"', ' [2991]={']:
            self.assertIn(record, catalog)
        self.assertGreater(catalog.count('category="vendor"'), 900)
        self.assertGreater(catalog.count('category="trainer"'), 500)


if __name__ == '__main__':
    unittest.main()
