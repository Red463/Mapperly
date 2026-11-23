"""Verify quest relations, conservative omissions, SQL schema and world axes."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('quest_locations_builder', ROOT / 'tools/build_quest_locations.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def fixture():
    return [
        ('quest_template', {'ID': '42'}),
        ('creature_template', {'entry': '9', 'name': "O'Neil"}),
        ('quest_objectives', {'ID': '101', 'QuestID': '42', 'Type': '0', 'ObjectID': '9', 'Visible': '1', 'Description': 'Defeat target'}),
        ('creature', {'guid': '1', 'id': '9', 'map': '0', 'position_x': '-10000', 'position_y': '-1000'}),
        ('creature_questender', {'id': '9', 'quest': '42'}),
    ]


class QuestLocationsTests(unittest.TestCase):
    def test_relation_and_axes_project_to_duskwood(self):
        quests, _ = b.extract(fixture())
        objective, turnin = sorted(quests[42], key=lambda r: r['kind'])
        self.assertEqual((objective['worldX'], objective['worldY'], objective['instance']), (-1000, -10000, 0))
        self.assertEqual(objective['objectiveID'], 101)
        self.assertNotIn('objectiveIndex', objective)
        self.assertEqual(turnin['label'], "O'Neil")
        # Native world map bounds: east axis determines normalized map x.
        left, right, top, bottom = 2000, -3000, -8000, -12000
        self.assertEqual(((left - objective['worldX']) / (left - right),
                          (top - objective['worldY']) / (top - bottom)), (.6, .5))

    def test_conditional_and_instance_spawns_are_omitted(self):
        for extra in ({'map': '33'}, {'PhaseId': '1'}, {'PhaseGroup': '2'},
                      {'phaseUseFlags': '1'}, {'terrainSwapMap': '0'},
                      {'spawnDifficulties': '0,1'}, {'position_x': 'nan'}):
            rows = fixture()
            rows[3][1].update(extra)
            self.assertEqual(b.extract(rows)[0], {}, extra)
        for table, row in [('game_event_creature', {'guid': '1'}),
                           ('pool_members', {'type': '0', 'spawnId': '1'})]:
            self.assertEqual(b.extract(fixture() + [(table, row)])[0], {})

    def test_no_inferred_item_or_wrong_quest_relations(self):
        rows = fixture()
        rows[2][1]['Type'] = '1'
        rows[-1][1]['quest'] = '999'
        self.assertEqual(b.extract(rows)[0], {})

    def test_turnin_faction_access_does_not_filter_enemy_objectives(self):
        rows = fixture()
        rows[1][1]['faction'] = '10'
        factions = {10: {'FactionGroup': '2', 'FriendGroup': '2', 'EnemyGroup': '4'}}
        quests, _ = b.extract(rows, factions)
        self.assertEqual(next(r['faction'] for r in quests[42] if r['kind'] == 'turnin'), 'A')
        quests, stats = b.extract(rows)
        self.assertEqual([r['kind'] for r in quests[42]], ['objective'])
        self.assertEqual(stats['excludedUnknownOrHostileTurninRelations'], 1)

    def test_singleton_poi_joins_idx1_and_explicit_objective(self):
        rows = fixture()
        poi = {'QuestID': '42', 'BlobIndex': '99', 'Idx1': '7', 'ObjectiveIndex': '4',
               'QuestObjectiveID': '101', 'MapID': '1'}
        point = {'QuestID': '42', 'Idx1': '7', 'Idx2': '0', 'X': '123', 'Y': '456'}
        rows += [('quest_poi', poi), ('quest_poi_points', point)]
        quests, _ = b.extract(rows)
        objective = next(r for r in quests[42] if r['kind'] == 'objective')
        self.assertEqual((objective['worldX'], objective['worldY'], objective['instance']), (456, 123, 1))
        self.assertEqual(objective['provenance'], 'quest_poi/quest_poi_points')
        self.assertNotIn('objectiveIndex', objective)
        # Area polygon, duplicate blob mapping or condition must use exact spawn fallback.
        for extra in [('quest_poi_points', dict(point, Idx2='1', X='124')),
                      ('quest_poi', dict(poi, BlobIndex='100'))]:
            q, _ = b.extract(rows + [extra])
            self.assertTrue(all(r['provenance'] != 'quest_poi/quest_poi_points' for r in q[42]))
        poi['PlayerConditionID'] = '1'
        q, _ = b.extract(rows)
        self.assertTrue(all(r['provenance'] != 'quest_poi/quest_poi_points' for r in q[42]))

    def test_caps_are_deterministic_and_disclosed(self):
        rows = fixture()
        for n in range(2, 30):
            rows.append(('creature', dict(rows[3][1], guid=str(n), position_y=str(n))))
        first, stats = b.extract(rows)
        second, _ = b.extract(reversed(rows))
        self.assertEqual(b.render(first), b.render(second))
        self.assertEqual(sum(r['kind'] == 'objective' for r in first[42]), b.MAX_PER_OBJECTIVE)
        self.assertEqual(sum(r['kind'] == 'turnin' for r in first[42]), b.MAX_TURNINS)
        self.assertGreater(stats['truncatedRecords'], 0)

    def test_declared_sql_schema_not_positional_guess(self):
        sql = """CREATE TABLE `quest_objectives` (
  `Description` text,
  `QuestID` int,
  `ID` int,
) ENGINE=InnoDB;
INSERT INTO `quest_objectives` VALUES ('O\\'Neil (east), target',42,101);
"""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.sql'
            path.write_text(sql, encoding='utf8')
            rows = list(b.services.rows(path, {'quest_objectives'}))
        self.assertEqual(rows[0][1], {'Description': "O'Neil (east), target", 'QuestID': '42', 'ID': '101'})


if __name__ == '__main__':
    unittest.main()
