"""Build a standalone named-quest catalog from the pinned public Forever SQL cache.
No runtime downloads, Questie imports, SQL server, or guessed pickup positions.
"""
from collections import Counter, defaultdict
import csv
import json
import subprocess
import build_services as services
import build_quest_locations as locations

ROOT = services.ROOT
MAX_STARTERS = 8
HOTFIX_SHA256 = "315e4b3bd2e2a0308f0fc5e746381e8733fe1d66b804b227b62f420681dcd36c"
TABLES = {"quest_template", "quest_template_addon", "quest_classic_level",
          "quest_template_classic_level", "creature_queststarter", "gameobject_queststarter",
          "creature", "gameobject", "creature_template", "gameobject_template",
          "gameobject_template_addon", "game_event_creature", "game_event_gameobject",
          "pool_members", "conditions", "disables", "spawn_group", "spawn_group_template"}
ADDON_FIELDS = ("MaxLevel", "PrevQuestID", "NextQuestID", "ExclusiveGroup", "RequiredSkillID",
                "RequiredSkillPoints", "RequiredMinRepFaction", "RequiredMinRepValue",
                "RequiredMaxRepFaction", "RequiredMaxRepValue", "SpecialFlags", "BreadcrumbForQuestId")
integer = locations.integer
# RaceMask.h GetRaceBit is not raceID-1 for newer races, including Forever Skyborne.
RACE_BITS = {race: race - 1 for race in list(range(1, 12)) + [22] + list(range(24, 33))}
RACE_BITS.update({34: 11, 35: 12, 36: 13, 37: 14, 52: 16, 70: 15,
                  84: 17, 85: 18, 86: 20, 91: 19, 95: 32, 96: 33})
SPECIAL_PICKUP_FLAGS = 0x400 | 0x1000 | 0x4000 | 0x8000 | 0x10000 | 0x80000 | 0x100000 | 0x800000 | 0x20000000


def race_ids(mask):
    if mask in (0, -1, (1 << 64) - 1):
        return None
    return sorted(race for race, bit in RACE_BITS.items() if mask & (1 << bit))


def ids(mask, width):
    """Decode with Python exact integers; never pass a uint64 mask through Lua floats."""
    if mask in (0, -1, (1 << width) - 1):
        return None
    return [i + 1 for i in range(width) if mask & (1 << i)]


def extract(input_rows, factions=None, hotfix_rows=()):
    factions = factions or {}
    data = defaultdict(list)
    stats = Counter()
    for table, row in input_rows:
        data[table].append(row)
        stats["input:" + table] += 1
    addons = {integer(r, "ID"): r for r in data["quest_template_addon"]}
    ranges = {integer(r, "ID"): r for r in data["quest_classic_level"]}
    levels = {integer(r, "ID"): r for r in data["quest_template_classic_level"]}
    conditional_quests = {abs(integer(r, "SourceEntry")) for r in data["conditions"]
                          if integer(r, "SourceTypeOrReferenceId") == 19}
    # Visibility source 32 can be by object kind; conservatively reject any matching entry.
    conditional_entries = {abs(integer(r, "SourceEntry")) for r in data["conditions"]
                           if integer(r, "SourceTypeOrReferenceId") == 32}
    disabled = {integer(r, "entry") for r in data["disables"] if integer(r, "sourceType") == 1}
    quests = {}
    for r in data["quest_template"]:
        title = (r.get("LogTitle") or "").strip()
        if not title:
            stats["excludedUnnamedQuests"] += 1
            continue
        qid = integer(r, "ID")
        q = dict(title=title, starters=[])
        addon = addons.get(qid, {})
        for field in ADDON_FIELDS:
            value = integer(addon, field)
            if value:
                q[field[0].lower() + field[1:]] = value
        for field, key in (("AllowableRaces", "raceIDs"), ("AllowableClasses", "classIDs")):
            value = (race_ids(integer(r, field)) if field == "AllowableRaces" else ids(integer(addon, field), 32))
            if value is not None:
                q[key] = value
        for field in ("Flags", "FlagsEx", "FlagsEx2", "FlagsEx3"):
            if integer(r, field):
                q[field[0].lower() + field[1:]] = integer(r, field)
        fixed = ranges.get(qid, {})
        if integer(fixed, "MinLevel") > 0:
            q["minLevel"] = integer(fixed, "MinLevel")
        if integer(fixed, "MaxLevel") > 0:
            q["maxLevel"] = integer(fixed, "MaxLevel")
        if integer(levels.get(qid, {}), "QuestLevel") > 0:
            q["level"] = integer(levels[qid], "QuestLevel")
        if integer(addon, "SpecialFlags") & 1 or integer(r, "Flags") & (0x1000 | 0x8000):
            q["repeatable"] = True
        if qid in disabled:
            q["disabled"] = True
        # Content tuning, scripts, conditions, chains and special interactions remain unknown.
        if (qid in conditional_quests or not q.get("minLevel") or addon.get("ScriptName")
                or any(integer(addon, k) for k in ("NextQuestID", "ExclusiveGroup", "BreadcrumbForQuestId",
                    "RequiredSkillID", "RequiredMinRepFaction", "RequiredMaxRepFaction", "SourceSpellID"))
                or integer(r, "AreaGroupID") or integer(r, "ManagedWorldStateID")
                or integer(r, "Flags") & SPECIAL_PICKUP_FLAGS or integer(r, "FlagsEx") or integer(r, "FlagsEx2") or integer(r, "FlagsEx3")):
            q["availabilityUnverified"] = True
        quests[qid] = q
    # NextQuestID also creates reverse dependency lists on the server. Do not ignore them.
    for qid, addon in addons.items():
        target = integer(addon, "NextQuestID")
        if target in quests:
            quests[target]["availabilityUnverified"] = True
    # ObjectMgr adds each source to every target along its breadcrumb path.
    # Direct signed IDs use abs on the server; subsequent links must be valid positive IDs.
    # Invalid targets/loops are not invented, and all involved named targets remain uncertain.
    actual_quests = {integer(r, "ID") for r in data["quest_template"]}
    breadcrumbs = defaultdict(set)
    for source, addon in sorted(addons.items()):
        if source not in actual_quests or source in disabled:
            continue
        target = abs(integer(addon, "BreadcrumbForQuestId"))
        visited = {source}
        while target:
            if target not in actual_quests or target in visited:
                break
            visited.add(target)
            if target in quests:
                breadcrumbs[target].add(source)
                quests[target]["availabilityUnverified"] = True
            next_target = integer(addons.get(target, {}), "BreadcrumbForQuestId")
            if next_target < 0:
                # Server's later signed-to-uint conversion is not a verified usable chain.
                break
            target = next_target
    for target, sources in sorted(breadcrumbs.items()):
        quests[target]["dependentBreadcrumbIDs"] = sorted(sources)
    stats["dependentBreadcrumbTargets"] = len(breadcrumbs)
    stats["dependentBreadcrumbRelations"] = sum(map(len, breadcrumbs.values()))
    names, template_factions, scripted = {}, {}, set()
    for kind in ("creature", "gameobject"):
        for r in data[kind + "_template"]:
            entry = integer(r, "entry")
            names[kind, entry] = r.get("name") or kind
            template_factions[kind, entry] = integer(r, "faction")
            if r.get("ScriptName"):
                scripted.add((kind, entry))
    for r in data["gameobject_template_addon"]:
        template_factions["gameobject", integer(r, "entry")] = integer(r, "faction")
    excluded = set()
    for kind in ("creature", "gameobject"):
        excluded.update((kind, integer(r, "guid")) for r in data["game_event_" + kind])
    for r in data["pool_members"]:
        if integer(r, "type") in (0, 1):
            excluded.add(("creature" if integer(r, "type") == 0 else "gameobject", integer(r, "spawnId")))
    conditional_groups = {integer(r, "groupId") for r in data["spawn_group_template"]
                          if integer(r, "groupFlags") & (0x04 | 0x20)}
    conditional_groups.update(abs(integer(r, "SourceEntry")) for r in data["conditions"]
                              if integer(r, "SourceTypeOrReferenceId") == 33)
    for r in data["spawn_group"]:
        if integer(r, "groupId") in conditional_groups and integer(r, "spawnType") in (0, 1):
            excluded.add(("creature" if integer(r, "spawnType") == 0 else "gameobject", integer(r, "spawnId")))
    spawns = defaultdict(list)
    for kind in ("creature", "gameobject"):
        for r in data[kind]:
            if integer(r, "map") not in services.MAPS:
                stats["excludedNonWorldSpawns"] += 1
                continue
            if (any(integer(r, k) for k in ("PhaseId", "PhaseGroup", "phaseUseFlags"))
                    or integer(r, "terrainSwapMap", -1) != -1
                    or (kind, integer(r, "guid")) in excluded
                    or (r.get("spawnDifficulties") or "0") != "0"
                    or integer(r, "id") in conditional_entries):
                stats["excludedConditionalSpawns"] += 1
                continue
            point = locations.coordinates(r)
            if point:
                spawns[kind, integer(r, "id")].append((integer(r, "map"), point, bool(r.get("ScriptName"))))
    for kind in ("creature", "gameobject"):
        for r in data[kind + "_queststarter"]:
            qid, entry = integer(r, "quest"), integer(r, "id")
            if qid not in quests:
                continue
            faction = locations.faction_access(template_factions.get((kind, entry), -1), factions)
            if not faction:
                stats["excludedUnknownOrHostileStarterRelations"] += 1
                continue
            for instance, point, scripted_spawn in spawns[kind, entry]:
                quests[qid]["starters"].append(dict(label=names.get((kind, entry), "Quest starter"),
                    worldX=point[0], worldY=point[1], instance=instance, faction=faction,
                    source="snapshot", provenance=kind + "_queststarter/" + kind))
                if scripted_spawn or (kind, entry) in scripted:
                    quests[qid]["availabilityUnverified"] = True
    for table, r in hotfix_rows:
        stats["input:" + table] += 1
        if table == "item_sparse" and integer(r, "StartQuestID") in quests:
            q = quests[integer(r, "StartQuestID")]
            q.setdefault("startItemIDs", []).append(integer(r, "ID"))
            q["availabilityUnverified"] = True  # Never invent a drop/vendor/position for an item.
    for q in quests.values():
        q["starters"] = locations.bounded(q["starters"], MAX_STARTERS, stats)
        if q.get("startItemIDs"):
            q["startItemIDs"] = sorted(set(q["startItemIDs"]))
        stats["starterRecords"] += len(q["starters"])
        stats["questsWithStarters"] += bool(q["starters"])
        stats["availabilityUnverifiedQuests"] += bool(q.get("availabilityUnverified"))
    stats["quests"] = len(quests)
    return dict(sorted(quests.items())), dict(sorted(stats.items()))


def lua(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dict):
        return "{" + ",".join(k + "=" + lua(v) for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "{" + ",".join(lua(v) for v in value) + "}"
    return json.dumps(value, ensure_ascii=False)


def render(quests):
    output = ["-- Generated by tools/build_quest_catalog.py; do not hand-edit.",
              "-- Forever TDB 2026-10-14; GPL-2.0. See QuestCatalog-SOURCES.md.",
              "local _,A=...", 'A.QuestCatalogData={version=1,source="Forever TDB 2026-10-14",quests={']
    output.extend(" [" + str(qid) + "]=" + lua(q) + "," for qid, q in sorted(quests.items()))
    search_order = sorted(quests, key=lambda qid: (quests[qid]["title"].lower(), qid))
    output.append("},searchOrder=" + lua(search_order) + "}")
    return "\n".join(output) + "\n"


def build():
    archive = services.CACHE / services.ARCHIVE
    locations.verify(archive, services.SHA256)
    sql, hotfix = services.CACHE / services.WORLD, services.CACHE / services.HOTFIX
    for path in (sql, hotfix):
        if not path.exists():
            subprocess.run(["tar", "-xf", str(archive), "-C", str(services.CACHE), path.name], check=True)
    locations.verify(sql, locations.SQL_SHA256)
    locations.verify(hotfix, HOTFIX_SHA256)
    faction_csv = ROOT / "tools/data/factiontemplate-70959.csv"
    locations.verify(faction_csv, "963a24a4a32acd76dea04ac337e037f45d72e2c6a403e3826dfcfc95e28b746d")
    with faction_csv.open(encoding="utf-8-sig", newline="") as f:
        factions = {int(r["ID"]): r for r in csv.DictReader(f)}
    quests, stats = extract(services.rows(sql, TABLES), factions, services.rows(hotfix, {"item_sparse"}))
    (ROOT / "Data/QuestCatalog.lua").write_text(render(quests), encoding="utf-8", newline="\n")
    print(json.dumps(stats, indent=2, sort_keys=True))


if __name__ == "__main__":
    build()
