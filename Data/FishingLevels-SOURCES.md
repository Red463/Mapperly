# Fishing skill reference

Source checked **24 November 2026**: [WCLBox Forever Fishing Areas by Skill](https://wowforever.wclbox.com/en/zhuanye/fishing), published for client build 1.60.1.71037. The table distinguishes minimum skill from reliable catches and states that lure skill counts.

`FishingLevels.lua` contains independently transcribed numerical reference facts and zone-to-map associations. It imports no addon code or database and requires no runtime download. The values are **published guidance, not official or server-verified requirements**. The tooltip preserves that distinction. These are open-water reference levels; pool mechanics and specific waters may differ. No base-skill formula from an emulator is assumed to apply to Forever.

| Minimum | Recommended | Covered waters |
| --- | --- | --- |
| 1 (after learning Fishing) | 25 | Original six starting zones |
| 1 | 75 | Original six capitals; Barrens, Loch Modan, Westfall, Silverpine, Darkshore |
| 51 | 150 | Duskwood, Wetlands, Redridge, Hillsbrad, Ashenvale, Stonetalon |
| 126 | 225 | Swamp of Sorrows, Dustwallow, Stranglethorn, Alterac, Arathi, Thousand Needles, Desolace |
| 201 | 300 | Azshara, Western Plaguelands, Hinterlands, Feralas, Felwood, Tanaris, Un'Goro, Moonglade; Jaguero Isle |
| 326 | 425 | Deadwind Pass, Burning Steppes, Eastern Plaguelands, Winterspring, Silithus; Jademir Lake and named high-skill Azshara waters |

The zone label shows ranges for Stranglethorn (Jaguero Isle), Feralas (Jademir Lake) and Azshara (Hetaera's Clutch, Bay of Storms, Scalebeard's Cave). The tooltip names these exceptions. It does not guess which water the cursor is over or assume that the entire zone uses the higher value.

Dungeon names in the source are omitted because reliable dungeon map coverage has not been established here. Badlands, Blasted Lands, Searing Gorge and Forever-specific zones without entries remain blank; absence does not assert that fishing is impossible. Overview maps do not receive fishing levels. No values are inferred from character quest levels or from The Fishing Log's observed catch-success bands.
