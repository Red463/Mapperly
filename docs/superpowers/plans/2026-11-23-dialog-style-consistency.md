# Dialog Style Consistency

User requests classic red buttons and Blizzard-textured backgrounds throughout settings/dialog windows. Apply only to Default theme; preserve Minimal Charcoal, native tabs and quiet note-icon choices.

Centralize action defaults in Dialogs.Action, with an explicit tab role at tab construction. Settings delegates to that helper. Synchronize native captions and disabled states immediately. Theme choices use red art with a selected checkmark. Card backgrounds use tiled native UI-Background-Rock over an opaque base; outer portrait dialogs retain their frame with warm tint and backing.

- [x] Add RED style/state tests for dialog buttons and textured cards.
- [x] Implement shared styles without changing route or data behavior.
- [x] Run dialog/theme/navigation regressions and fresh review.
- [x] Package and verify preview.19. Live visual acceptance remains pending.
