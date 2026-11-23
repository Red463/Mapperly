# Mapperly 1.2.0-rc.7: welcome and update notices

Replace the Mapperly folder with the one from Mapperly-1.2.0-rc.7.zip and reload.

- Existing installation: What's new in Mapperly should appear once after loading. Close it with Got it, the X, or Escape. Reload or switch characters: it should not repeat.
- New installation: Welcome to Mapperly! should give a short overview. There must not be a second update window for that same version.
- Combat or an open Mapperly settings/note/navigation dialog should delay the notice without marking it seen. Close the other dialog or leave combat and it should appear.
- Check Default and Minimal Charcoal. Headings, body text and Got it must fit, including at your normal UI scale.

## Optional preview/reset commands

These reset only the popup tracking, keeping notes, destinations and settings.

To test the welcome on an existing installation:

```lua
/run MapperlyDB.announcementState={welcomeSeen=false,versions={}}; ReloadUI()
```

To test this version's update notes again:

```lua
/run MapperlyDB.announcementState={welcomeSeen=true,versions={}}; ReloadUI()
```

After closing either window, reload again without a reset command to confirm it stays dismissed. Automatic display waits briefly after entering the world. A fresh user's deferred welcome remains pending through reload/logout until it can be displayed.

## Maintaining future update notes

Add the new TOC version to docs/release-highlights.md with one to four short player-facing bullets. tools/package.py regenerates Data/ReleaseNotes.lua and rejects missing or overlong highlights. Keep technical implementation details in CHANGELOG.md.
