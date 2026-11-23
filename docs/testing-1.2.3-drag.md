# Mapperly 1.2.3: native movable-state hotfix

Install Mapperly-1.2.3.zip and `/reload` to clear the drag guard left by an earlier failed attempt. Saved positions/settings do not need resetting.

- With Lock map position off, open the map and drag its title bar. Repeat after switching sizes/themes and after opening the closed map in combat.
- Release the map and check its saved position survives closing/reopening. Check both compact/enlarged views and quest-pane choices.
- The reported `WorldMapFrame:StartMoving(): Frame is not movable` error must not appear. After any rejected attempt, settings and later drags must remain responsive.
- Lock map position must still prevent movement. Genuinely protected frames retain native combat restrictions.
- If movement is still refused, run `/mapperly mapreport start`, attempt one drag and export `/mapperly mapreport`. Active captures now record `drag-start-failed` along with native movable/protected state.

Regression: the earlier drag code assumed the flag set by out-of-combat layout was still true. Native display updates or first combat opening can leave an unlocked frame non-movable. The new handler restores and checks native state before StartMoving, and rejects failures without leaving A.dragging set.
