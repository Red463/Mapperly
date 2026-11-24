# Mapperly 1.2.4: What's new layout

Install Mapperly-1.2.4.zip and `/reload`. The update window should show a version heading, inset highlight rows with small native check marks, and a footer/button close to the content. Short notes must no longer float in a large empty text area.

- Check Default and Minimal Charcoal at normal UI scale. Text should begin at the top of each row, wrap without clipping and leave clear margins around the check mark and frame edges.
- Confirm the Got it button and settings-preserved footer fit below the last row. The existing native close button and Escape must still dismiss the window.
- Confirm it appears once for this version across characters and waits during combat or another Mapperly dialog.
- The welcome window retains its brief overview and existing size, with top-aligned text.

If this version was already dismissed while testing, this command resets only the announcement history for a repeat preview; it keeps settings, notes and destinations:

```lua
/run MapperlyDB.announcementState={welcomeSeen=true,versions={}}; ReloadUI()
```

Automated coverage exercises one to four wrapped highlights, grows the window with content, checks footer/button bounds, both themes, fallback notes, and existing announcement timing/history. Final native font rendering still needs the in-game check above.
