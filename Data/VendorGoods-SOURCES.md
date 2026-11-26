# Vendor goods

The directory contains 12,418 regular vendor/item pairs for 892 of Mapperly’s 931 distinct outdoor merchant NPCs. Items are stored once by ID, with a category, an English name and a native client icon file ID. Merchants with no matched stock remain available by NPC name. Of 1,564 distinct items in the filtered stock, 1,485 had a match with all three fields.

## Sources

- **Merchant stock.** `npc_vendor.entry` and `npc_vendor.item` from the [Forever TDB release dated 2026-10-14](https://github.com/Karrz1/TrinityCore/releases/tag/forever-tdb-2026-10-14). The generator verifies the archive, world SQL and hotfix SQL hashes already recorded in [QuestCatalog-SOURCES.md](QuestCatalog-SOURCES.md). The existing [ServiceDirectory filters](ServiceDirectory-SOURCES.md) supply eligible NPC IDs and coordinates.
- **Item facts.** The English WoW Forever client build 1.60.1.70959 supplies `Item`, `ItemSparse`, `ItemXItemEffect`, `ItemEffect` and `SpellName`. The addon refers to existing client icons by numeric ID. It does not redistribute item textures. Earlier SQL hotfix item records can fill gaps in the base item/name tables.
- **Access and stock.** The builder retains positive item IDs with vendor type 1. It excludes currency, references, `PlayerConditionID` requirements, and any vendor/item pair gated by `conditions` source type 23. Event-only stock from `game_event_npc_vendor` is excluded. An item may be limited in quantity, require special currency or be unusable by the character. This is a snapshot of what a vendor sells, not a live stock count.
- **Categories.** The client’s item classes and subclasses distinguish ammunition, equipment, bags (including quivers), crafting supplies, reagents (including miscellaneous subclass 1), recipes, mounts and companion pets. Food and drink share subclass 0/5. The builder checks on-use recovery categories 11 and 59, food/alcohol effects and the pet-food type to distinguish them. Unresolved consumables remain under Consumables.

For example, the snapshot lists Sharp Arrow, Heavy Shot, Small Brown Pouch and Simple Wood at Dalmond in Auberdine, and Moist Cornbread and Melon Juice at Kyndri. Both merchants sell Refreshing Spring Water.

Fishing poles use weapon subclass 2/20 in the client and get their own Fishing category. Shiny Bauble, Nightcrawlers, Bright Baubles, Aquadynamic Fish Attractor and Aquadynamic Fish Lens are classified as tackle. The client’s on-use spells 8087, 8088, 8090, 8089 and 8532 apply the corresponding temporary fishing-pole enchants. The Mining Pick, Blacksmith Hammer and Skinning Knife are listed with trade supplies.

## Reproduction

Use the SQL archive, faction CSV and source builder documented in [ServiceDirectory-SOURCES.md](ServiceDirectory-SOURCES.md). Export these English DB2s from client build 70959 using DBC2CSV. The source CSV hashes are pinned in `tools/build_vendor_goods.py`.

| Table | File data ID | SHA-256 of native DB2 |
| --- | ---: | --- |
| Item | 841626 | `8cc2345c211ad11dc3358ab6e982c3b7dda932deac094ac730ccb81c663a1058` |
| ItemSparse | 1572924 | `fd11f17ec11be177dc30db40d70d117c2f2712740b5c72c4becd096cbccbb89f` |
| ItemXItemEffect | 3177687 | `d655027fd09500eaa8c986d5088289b772fe1e0980e0fca68966dea617ec3c18` |
| ItemEffect | 969941 | `adc7d2b98eeabe107bb3c2cb8cbbad87008daE23bb1f90d12cb47d63d236f39e` |
| SpellName | 1990283 | `282155df6a490001f6c0899404097726720b853764ae12130bb1fd40fa4adc44` |

Run `python tools/build_vendor_goods.py --tables <directory-of-English-CSVs> --spell-names <spellname.csv>`, then `python tests/vendor_goods.py`. The generated Lua is the only new goods file the client loads. No additional addon, item cache warm-up or network request is required.
