Mapperly 1.2.3 fixes the map-drag error **WorldMapFrame:StartMoving(): Frame is not movable**.

- Restore and verify the native movable flag before dragging an unlocked map. Native display changes can clear this flag independently of Mapperly's Lock map position option.
- Safely handle rejected or partially started movement, clear the dragging guard and process deferred layout without saving a failed drag position.
- Keep Lock map position and genuine protected-frame combat restrictions. Active `/mapperly mapreport` captures record rejected drag starts for diagnosis.

Install **Mapperly-1.2.3.zip** and run `/reload` or restart the game. Reload clears any dragging state left by a previous error; saved positions, settings, notes and destinations are preserved.

Validation: **107 automated test suites passed**, including reproduction of the exact reported exception, both map sizes/themes, in/out-of-combat movement, forced refusal and failed-start cleanup. Release ZIP integrity and source checks also passed.

See the [drag test guide](testing-1.2.3-drag.md) for in-game checks and diagnostic instructions.
