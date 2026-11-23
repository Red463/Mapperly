"""Catalog schema, native relations, exact masks, availability and filtering checks."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_quest_catalog as b


def fixture():
    return [
        ("quest_template", {"ID": "42", "LogTitle": "A named quest", "Flags": "8"}),
        ("quest_classic_level", {"ID": "42", "MinLevel": "5", "MaxLevel": "20"}),
        ("quest_template_classic_level", {"ID": "42", "QuestLevel": "10", "LevelType": "2"}),
        ("creature_template", {"entry": "9", "name": "O'Neil", "faction": "0"}),
        ("creature", {"guid": "1", "id": "9", "map": "0", "position_x": "-10000", "position_y": "-1000"}),
        ("creature_queststarter", {"id": "9", "quest": "42"}),
    ]


class CatalogTests(unittest.TestCase):
    def test_schema_uses_declared_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "source.sql"
            p.write_text("CREATE TABLE `quest_template` (\n  `LogTitle` text,\n  `ID` int\n);\nINSERT INTO `quest_template` VALUES ('A title',42);\n")
            rows = list(b.services.rows(p, {"quest_template"}))
            self.assertEqual(rows, [("quest_template", {"LogTitle": "A title", "ID": "42"})])

    def test_level_and_axes_and_starter_provenance(self):
        q = b.extract(fixture())[0][42]
        self.assertEqual((q["level"], q["minLevel"], q["maxLevel"]), (10, 5, 20))
        self.assertNotIn("availabilityUnverified", q)  # Sharable is not an availability condition.
        starter = q["starters"][0]
        self.assertEqual((starter["worldX"], starter["worldY"], starter["instance"]), (-1000, -10000, 0))
        self.assertEqual(starter["provenance"], "creature_queststarter/creature")
        self.assertEqual(starter["label"], "O'Neil")
        self.assertEqual(starter["source"], "snapshot")

    def test_all_named_quests_including_missing_starters(self):
        rows = fixture() + [("quest_template", {"ID": "99", "LogTitle": "No positions"}),
                            ("quest_template", {"ID": "100", "LogTitle": ""})]
        quests, stats = b.extract(rows)
        self.assertEqual(set(quests), {42, 99})
        self.assertEqual(quests[99]["starters"], [])
        self.assertTrue(quests[99]["availabilityUnverified"])
        self.assertEqual(stats["excludedUnnamedQuests"], 1)

    def test_availability_fields_and_exact_remapped_races(self):
        rows = fixture()
        rows[0][1]["AllowableRaces"] = str((1 << 63) | (1 << 32) | 1)
        rows.append(("quest_template_addon", {"ID": "42", "PrevQuestID": "-33", "AllowableClasses": "3",
            "RequiredSkillID": "164", "RequiredSkillPoints": "150", "RequiredMinRepFaction": "72",
            "RequiredMinRepValue": "3000", "SpecialFlags": "1"}))
        q = b.extract(rows)[0][42]
        self.assertEqual(q["raceIDs"], [1, 95])  # Race 95 uses bit 32, not bit 94.
        self.assertEqual(q["classIDs"], [1, 2])
        self.assertEqual(q["prevQuestID"], -33)
        self.assertEqual(q["requiredSkillPoints"], 150)
        self.assertEqual(q["requiredMinRepValue"], 3000)
        self.assertTrue(q["repeatable"])
        self.assertTrue(q["availabilityUnverified"])
        self.assertIsNone(b.race_ids(2 ** 64 - 1))
        self.assertEqual(b.race_ids(1 << 33), [96])

    def test_no_guessed_tuning_level_or_item_location(self):
        rows = fixture()
        rows = [r for r in rows if r[0] not in ("quest_classic_level", "quest_template_classic_level", "creature_queststarter")]
        rows[0][1]["ContentTuningID"] = "123"
        q = b.extract(rows, hotfix_rows=[("item_sparse", {"ID": "7", "StartQuestID": "42"})])[0][42]
        self.assertNotIn("minLevel", q)
        self.assertNotIn("level", q)
        self.assertEqual(q["startItemIDs"], [7])
        self.assertEqual(q["starters"], [])

    def test_conditional_and_wrong_world_spawns_never_remove_names(self):
        for extra in ({"map": "33"}, {"PhaseId": "1"}, {"PhaseGroup": "2"}, {"phaseUseFlags": "1"},
                      {"terrainSwapMap": "0"}, {"spawnDifficulties": "0,1"}, {"position_x": "nan"}, {"id": "9,10"}):
            rows = fixture()
            rows[4][1].update(extra)
            if extra.get("id"):
                # This schema uses one integer ID; malformed multi-template data must fail closed.
                with self.assertRaises(ValueError):
                    b.extract(rows)
            else:
                self.assertEqual(b.extract(rows)[0][42]["starters"], [], extra)
        for row in [("game_event_creature", {"guid": "1"}),
                    ("pool_members", {"type": "0", "spawnId": "1"}),
                    ("conditions", {"SourceTypeOrReferenceId": "32", "SourceEntry": "9"})]:
            self.assertEqual(b.extract(fixture() + [row])[0][42]["starters"], [])

    def test_manual_or_condition_controlled_spawn_groups(self):
        for marker in [("spawn_group_template", {"groupId": "7", "groupFlags": "4"}),
                       ("spawn_group_template", {"groupId": "7", "groupFlags": "32"}),
                       ("conditions", {"SourceTypeOrReferenceId": "33", "SourceEntry": "7"})]:
            rows = fixture() + [marker, ("spawn_group", {"groupId": "7", "spawnType": "0", "spawnId": "1"})]
            self.assertEqual(b.extract(rows)[0][42]["starters"], [])
        rows = fixture() + [("spawn_group_template", {"groupId": "7", "groupFlags": "9"}),
                            ("spawn_group", {"groupId": "7", "spawnType": "0", "spawnId": "1"})]
        self.assertEqual(len(b.extract(rows)[0][42]["starters"]), 1)

    def test_conditions_and_reverse_chain_and_disabled(self):
        rows = fixture() + [("conditions", {"SourceTypeOrReferenceId": "19", "SourceEntry": "42"})]
        self.assertTrue(b.extract(rows)[0][42]["availabilityUnverified"])
        rows = fixture() + [("quest_template_addon", {"ID": "99", "NextQuestID": "42"}),
                            ("disables", {"sourceType": "1", "entry": "42"})]
        q = b.extract(rows)[0][42]
        self.assertTrue(q["availabilityUnverified"])
        self.assertTrue(q["disabled"])

    def test_reverse_breadcrumbs_include_actual_sources_and_transitive_targets(self):
        rows = fixture() + [
            ("quest_template", {"ID": "33", "LogTitle": "Breadcrumb one"}),
            ("quest_template", {"ID": "34", "LogTitle": "Breadcrumb two"}),
            ("quest_template", {"ID": "35", "LogTitle": "Final target"}),
            ("quest_template_addon", {"ID": "33", "BreadcrumbForQuestId": "42"}),
            ("quest_template_addon", {"ID": "34", "BreadcrumbForQuestId": "42"}),
            ("quest_template_addon", {"ID": "42", "BreadcrumbForQuestId": "35"}),
            ("quest_template_addon", {"ID": "999", "BreadcrumbForQuestId": "42"}),
        ]
        quests, _ = b.extract(rows)
        self.assertEqual(quests[42]["dependentBreadcrumbIDs"], [33, 34])
        self.assertEqual(quests[35]["dependentBreadcrumbIDs"], [33, 34, 42])
        self.assertTrue(quests[42]["availabilityUnverified"])
        self.assertEqual(b.render(quests), b.render(b.extract(list(reversed(rows)))[0]))

    def test_reverse_breadcrumb_sign_zero_invalid_disabled_and_cycle(self):
        rows = fixture() + [
            ("quest_template", {"ID": "33", "LogTitle": "Breadcrumb"}),
            ("quest_template", {"ID": "34", "LogTitle": "Invalid target"}),
            ("quest_template", {"ID": "35", "LogTitle": "Disabled source"}),
            ("quest_template_addon", {"ID": "33", "BreadcrumbForQuestId": "-42"}),
            ("quest_template_addon", {"ID": "34", "BreadcrumbForQuestId": "999"}),
            ("quest_template_addon", {"ID": "35", "BreadcrumbForQuestId": "42"}),
            ("disables", {"sourceType": "1", "entry": "35"}),
        ]
        quests, _ = b.extract(rows)
        self.assertEqual(quests[42]["dependentBreadcrumbIDs"], [33])
        self.assertNotIn("dependentBreadcrumbIDs", quests[34])
        self.assertTrue(quests[34]["availabilityUnverified"])
        self.assertNotIn("dependentBreadcrumbIDs", b.extract(fixture())[0][42])
        rows.append(("quest_template_addon", {"ID": "42", "BreadcrumbForQuestId": "33"}))
        quests, _ = b.extract(rows)
        self.assertEqual(quests[42]["dependentBreadcrumbIDs"], [33])
        self.assertEqual(quests[33]["dependentBreadcrumbIDs"], [42])

    def test_gameobject_starter_and_hostile_faction(self):
        rows = [(t.replace("creature", "gameobject"), r.copy()) for t, r in fixture()]
        rows.append(("gameobject_template_addon", {"entry": "9", "faction": "123"}))
        factions = {123: {"FactionGroup": "2", "FriendGroup": "2", "EnemyGroup": "4"}}
        self.assertEqual(b.extract(rows, factions)[0][42]["starters"][0]["faction"], "A")
        factions[123]["EnemyGroup"] = "6"
        factions[123]["FactionGroup"] = "0"
        factions[123]["FriendGroup"] = "0"
        self.assertEqual(b.extract(rows, factions)[0][42]["starters"], [])

    def test_cap_samples_existing_positions_and_is_deterministic(self):
        rows = fixture()
        rows += [("creature", {"guid": str(i + 2), "id": "9", "map": "0", "position_x": str(-9000 + i),
                               "position_y": "-1000"}) for i in range(20)]
        quests, stats = b.extract(rows)
        self.assertEqual(len(quests[42]["starters"]), 8)
        original = {float(r[1]["position_x"]) for r in rows if r[0] == "creature"}
        self.assertTrue(all(r["worldY"] in original for r in quests[42]["starters"]))
        self.assertEqual(stats["truncatedRecords"], 13)
        self.assertEqual(b.render(quests), b.render(b.extract(list(reversed(rows)))[0]))

    def test_search_order_is_deterministic_case_insensitive_and_complete(self):
        sys.path.insert(0, str(ROOT / ".test-deps"))
        from lupa.lua51 import LuaRuntime
        lua = LuaRuntime(unpack_returned_tuples=True)
        quests = {9: {"title": "zeta", "starters": []}, 4: {"title": "Alpha", "starters": []},
                  2: {"title": "alpha", "starters": []}}
        lua.execute('A={}; assert(loadstring(...))("Mapperly",A)', b.render(quests))
        order = list(lua.globals().A.QuestCatalogData.searchOrder.values())
        self.assertEqual(order, [2, 4, 9])
        self.assertEqual(set(order), set(quests))
        self.assertEqual(len(order), len(quests))

    def test_generated_lua_loads_and_retains_all_quest_names(self):
        sys.path.insert(0, str(ROOT / ".test-deps"))
        from lupa.lua51 import LuaRuntime
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute('A={}; assert(loadstring(...))("Mapperly",A)', (ROOT / "Data/QuestCatalog.lua").read_text(encoding="utf8"))
        lua.execute('assert(A.QuestCatalogData.version==1); assert(A.QuestCatalogData.quests[1844].dependentBreadcrumbIDs[1]==1840); assert(A.QuestCatalogData.quests[1844].availabilityUnverified); local n,s=0,0; for id,q in pairs(A.QuestCatalogData.quests) do n=n+1; assert(q.title~="" and type(q.starters)=="table"); s=s+#q.starters; assert(#q.starters<=8) end; assert(n==48793 and s==4123); local seen={}; assert(#A.QuestCatalogData.searchOrder==n); for _,id in ipairs(A.QuestCatalogData.searchOrder) do assert(A.QuestCatalogData.quests[id] and not seen[id]); seen[id]=true end; for id in pairs(A.QuestCatalogData.quests) do assert(seen[id]) end')


if __name__ == "__main__":
    unittest.main()
