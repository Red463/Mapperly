# Nearby vendors and trainers

Mapperly bundles 935 vendor and 546 trainer locations from the public Forever TDB snapshot dated October 14, 2026. Of the vendor locations, 316 offer gear repairs. These records supply the nearby-services drawer. Inns and mailboxes come from the existing [service dataset](Services-SOURCES.md).

| World | Vendor locations | Trainer locations |
| --- | ---: | ---: |
| Eastern Kingdoms | 483 | 275 |
| Kalimdor | 415 | 238 |
| Zephras Isle | 37 | 33 |

The snapshot supplies the NPC name, spawn coordinates and, when present, the specialty shown underneath the NPC's name in game. A location can offer multiple services. For example, Innkeeper Trelayne also sells goods. Coordinates represent the spawn location, so moving merchants can wander from the listed point. Reputation, profession and class requirements may affect the services offered to a particular player.

## Source and selection

- The builder verifies the existing pinned archive and world SQL hashes from [the quest-location extraction](QuestLocations-SOURCES.md). The database-derived records are distributed under GPL version 2. [Forever TDB release](https://github.com/Karrz1/TrinityCore/releases/tag/forever-tdb-2026-10-14) · [Bundled license](../Libs/Forever-Services-COPYING.txt)
- It joins `creature.id` to `creature_template.entry` and uses the spawn's `npcflag` override when present, including an explicit zero. The vendor role uses the five vendor bits from the server's vendor mask. The trainer role uses the generic, class and profession trainer flags. The repair flag (0x1000) qualifies a spawn for gear repairs independently of merchandise or trainer specialty. Repair vendors share their merchant record. A trainer's nonzero `trainer_class` are retained. [Forever NPC flag definitions](https://github.com/Karrz1/TrinityCore/blob/forever/src/server/game/Entities/Unit/UnitDefines.h)
- The build accepts normal world spawns on instances 0, 1 and 2991. It excludes explicit phases, terrain swaps, nondefault difficulties, event or pooled spawns, visibility conditions, and manually or conditionally activated spawn groups. Identical NPC, service and world positions are collapsed.
- Faction eligibility uses the same pinned Forever faction table and selection rules as the inn dataset. NPCs with unknown faction access or hostile to both sides are omitted. Among the selected records, 430 vendors are Alliance, 330 Horde and 175 shared. For trainers, those counts are 260, 236 and 50.
- `A.ServiceDirectory` groups records by native world instance. `x` is SQL north and `y` is SQL east, in yards. HereBeDragons accepts these as `(y, x)`. The source's `zoneId` and `areaId` are zero for every world spawn, so the game map is resolved from world coordinates at runtime.

## Reproduction

With the archive in `assets/services-source`, run `python tools/build_service_directory.py` from the Mapperly directory. Then run `python tests/service_directory_builder.py` to check extraction rules and known NPCs on both continents. The large archive and SQL are only build inputs. The installed addon reads the bundled Lua data locally.
