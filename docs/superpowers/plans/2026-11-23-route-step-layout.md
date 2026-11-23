# Route Step Layout and Labels

User requests more space between text and frame edges, travel-method icons, and short labels such as Fly to X instead of verbose boarding instructions.

Use 20px content insets in the existing 312px no-portrait panel. Row frames are 272px wide, at least 28px tall, with 18px icons and a separate padded text column. Use existing transparent signpost/travel, winged boot and passenger-vessel art. Highlight the full current row; keep completed labels/icons muted. Retain ten-step windowing, small-screen fitting, saved position/collapse and read-only journey behavior.

Format transport rows from typed transport.kind/toName. Current and future rows use the same concise label; detailed current instructions stay in a hover tooltip. Forward row drags to the existing panel drag handlers.

- [x] RED test for concise labels, method icons and padded rows.
- [x] Implement labels/row frames, tooltip and drag forwarding.
- [x] Run UI/navigation regressions and independent review.
- [x] Package and verify preview.21. Live visual acceptance remains pending.
