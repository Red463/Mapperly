# Switchable Mapperly theme implementation plan

> Use superpowers:executing-plans inline with one fresh final review.

Goal: implement the approved Gatherly-style mockup with Original preserved as a live-selectable setting.
Spec: user-approved assets/theme-mockup/map.png and dialogs.png. Use warm grey panels, native stone/bronze portrait chrome, cream/gold type, muted fields, native red primary actions, compact right rail and a largely borderless map. Preserve all existing map, note and navigation behavior. No Gatherly runtime dependency.
Architecture: Theme.lua owns theme validation/application, a registry of styled regions and native template helpers. Existing widget factories register surfaces and labels. Settings exposes two explicit choices above both pages. Store persists theme; default is gatherly. Switching is in place, preserving visibility, focus, edits, scroll and current tab.

- [x] 1. RED: persisted theme and live-switch tests. Add Theme.lua, settings selection, shared dialog surfaces, labels and native chrome. Test default/invalid/saved values, existing windows and late-created windows.
- [x] 2. RED: primary buttons, tabs, map and quest background restoration. Style shared controls and map chrome without changing marker art, sizing or click handlers. Test Original restoration and repeated toggles.
- [x] 3. Run complete regressions and fresh review. Document the selector and defaults; build local 1.2.0 ZIP and verify TOC/assets. Do not publish.

Review focus: full reversibility; template fallback; no interference with editor state or callbacks; map canvas frame/strata levels; native quest background lifecycle; small-screen selector fit.

## Ledger
- Work continues on the existing feature branch, preserving all prior uncommitted changes.
- Shared interfaces checked: Buttons uses Theme only after module load; UI factories run after InitStore. Theme application must not rebuild windows or call their Show helpers.

- Tasks 1/2: themes.py and run.py RED -> GREEN. Theme persistence, invalid values, selector, open drafts, primary actions, fallback title, map trim and native quest alpha restoration verified. Existing UI/navigation suites remain green.

- Final fresh review found incomplete-template title and tab paths; themes.py reproduced both RED, then GREEN after title capability checks and guarded installed tab-helper validation. Unsupported native art is hidden and cached as unavailable.
- Original inherited text/shadow restoration was included in the same fix pass as required theme reversibility; explicit custom-colour/shadow regression RED -> GREEN. No review findings remain deferred for this theme change.
- Full seven-suite regression run and local 1.2.0 ZIP verification complete. Source remains local; no push or publication.
