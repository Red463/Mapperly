# Preview.36: finding quests not accepted yet

Install preview.36 and reload. Open **Destinations > Quests**, then choose **Find quests**. **Active** retains the existing accepted-quest workflow.

1. Enter at least two letters of an English quest name, or an exact numeric quest ID. Press Enter to search immediately or pause briefly while typing. Broad searches show at most100results and ask you to narrow the query.
2. Inspect the status: **Possible pickup** means modeled checks passed against snapshot data; **Unavailable** means a known restriction; **Availability unconfirmed** means additional requirements or live data cannot be established. Hover for the reason.
3. Choose **Locations**. A known starter should show its zone, coordinates and snapshot source. **Preview** and **Go** use normal routing, including clearly labeled nearby approaches where exact points are blocked. Unconfirmed pickups can route to the recorded starter, with an in-game reminder that acceptance is not guaranteed.
4. Search a quest above your level, one already completed, one restricted to another class/race/faction, and a chain step whose prerequisite is unfinished. Known restrictions should disable pickup routing and explain why. Repeatable resets, skills, reputation and unsupported conditions remain explicitly unconfirmed.
5. Preview a pickup, then accept or complete that quest before pressing Start. The old pickup action must be rejected. Accepted quests should appear in **Active**, rather than Find quests results.
6. Search a quest with no recorded starter or an item-started quest. It must explain the missing location; no guessed drop/vendor/instance coordinates should appear.
7. Return to **Active** and test an objective and a turn-in. Coordinates, Saved and Recent must still work, in both themes.

The catalogue is a pinned public Forever development snapshot, not a live realm export. It includes unused, disabled and otherwise inaccessible templates.48,793 names are searchable; only3,702quests have verified starter positions. Source limits and supported condition semantics are documented in `Data/QuestCatalog-SOURCES.md`. Never interpret a search result as guaranteed live availability.
