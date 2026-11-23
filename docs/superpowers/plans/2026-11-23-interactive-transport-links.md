# Interactive transport links (checklist 11)

The user approved completing continent transport connections: boat, zeppelin, airship and discovered flight links, independent hover highlighting and click-to-preview/start a destination journey. Existing modifier clicks and location filters persist. Trams remain unverified and excluded.

## Design

Use current `Transports.Edges` as the availability authority (saved methods, faction, build, flight discovery/fare eligibility). A small `TransportLinks` adapter binds markers to outgoing directed rows, validates stale selections and converts a chosen destination into an ordinary journey request. It does not invent discovery or require taking the clicked service; the journey planner chooses among enabled travel methods to that destination.

Extend native transport markers to zeppelins/airships; retain stable flight-node identity on native flight markers. Hover all available outgoing connections. The existing boat overlay becomes a general transport overlay while retaining its compatibility name and caps, layering, native geometry breaks and map isolation. Azeroth uses schematic dashed endpoint links; native geometry is used when available on continent maps, with explicitly schematic endpoint links for unavailable/cross-instance geometry.

Click opens a themed destination list with source, method, destination, estimated transport time and recorded fare. Each row has Preview and Navigate actions. The list uses the existing scrollable dialog controls and matching icons. Hovering list rows highlights one connection; leaving restores/clears highlights without changing navigation. Controls revalidate availability when activated. Normal Ctrl-click pings, Alt-right-click navigation and right-click map zoom remain unchanged.

Faint background connections have a separate default-on Navigation display preference, subject to the unchanged location-layer and On continents filters. Background rendering is capped at 48 candidate connections/384 lines, with separate capacity reserved for active and hover overlays. Dense native paths use bounded sampling that still inspects every geometry break. World endpoint schematics do not build unnecessary native flight geometry.

## Steps and checks

1. Add availability/binding/action adapter and RED/GREEN tests for filters, faction/discovery delegation, stale row rejection and unchanged journey on hover/preview.
2. Extend native markers and overlay to supported modes, identity-preserving deduplication and safe geometry; cover world/continent/zone views and pin recycling.
3. Add destination chooser and native click/tooltip integration; test scrolling, buttons, modifiers, live availability changes and error display.
4. Run relevant and complete regressions, independent review, update checklist/docs and package preview.30. No GitHub publication requested.

## Outcome

Implemented the adapter, native marker identity, general transport overlay, background display setting and themed destination chooser. All 59 suites pass, including four new interactive-link suites. Review found the initial continent background used schematic shortcuts; the corrected renderer retains native pieces and all breaks. Off-map sources are filtered before the rendering budget, with an additional regression. Final review found no remaining important issues. Live in-game appearance/click acceptance remains pending.
