# Current button design: Dark charcoal icon rail

The user requested slightly darker flat buttons, all actions on the map?s right side, generated icons matching the painted map markers, retained tooltips, and a smaller footprint.

Buttons.lua keeps solid charcoal faces (normal RGB .105/.11/.12), borderless faces, brighter hover fills, darker pressed fills and gold active highlights. Icon buttons are 28?28 UI units with centered 24-unit artwork and two-unit padding. The quest symbol also uses 24-unit artwork with its small direction arrow. No gradients or bevels are added to button faces.

Map.lua places all ten actions in a vertical rail: Close, Resize, Parent map, My location, Add note, Filters, Quest log, Reveal, Lock, Settings. Gaps separate navigation, layers and preferences. Tooltips name every action; resize, quest, reveal and lock tips describe the current action. Zone name and level range remain in a noninteractive header label.

Shell.lua reserves 32 units at the right edge of the window for the rail, outside both map artwork and quest content. Both map sizes preserve a 3:2 canvas. The native quest panel retains its width and gutters. The rail is above map content but below dialog windows.

Nine icons were generated using the built-in image_gen tool: Locate, AddNote, Filters, Reveal, Lock, Settings, Resize, Close and ParentMap. Original transparent PNGs and exact prompts are saved in assets/toolbar. Quest reuses assets/Quest.png from the existing generated marker family. The builder writes 128, 64 and 32 pixel uncompressed RGBA TGA variants to Media/Toolbar. At runtime small textures are used to avoid shrinking a large image unnecessarily.

Tests cover icon rail membership and size, tooltips, dropdown anchor, flat colour, active states, map/quest layout across screen sizes, note creation/deletion, opacity and all 30 toolbar texture variants. The preview at output/mapperly-toolbar-icons-preview.png shows 48px and 20px assets on charcoal. Actual client rendering still needs in-game verification.

Version 0.1.21 replaces the funnel with generated stacked parchment layers and a checkmark. The source PNG is assets/toolbar/Filters-v2.png; the exact built-in image_gen prompt is in Filters-v2-prompt.json. Earlier source artwork is retained. The current borderless preview is output/mapperly-toolbar-borderless-preview.png.

The footer uses two non-wrapping columns, ten-unit outside padding and at least a twelve-unit center gap. Player coordinates are left-aligned; cursor coordinates are right-aligned, with -- placeholders outside map bounds. The opaque footer uses HIGH strata and map-relative level +2500 to cover older map-coordinate labels underneath the strip without modifying other addon settings or data. Regression tests cover coordinate formatting, unavailable cursor position, hidden coordinates and column width at each tested map size. In-game checks are still needed for the installed addon mix.

Version 0.1.22 adds a separate generated Compact icon with inward-pointing arrows. UpdateButtonStates selects Resize (outward) in compact mode and Compact (inward) in enlarged mode, matching the next action and tooltip. Texture changes are cached instead of reapplying on every polling update. Tests alternate modes and verify both paths; all 33 toolbar textures have valid RGBA transparency.

Version 1.1.0 places the two coordinate readouts together in one left-aligned, non-wrapping footer line with a pipe separator. The line reserves ten units of padding on each side and uses the full available footer width.
