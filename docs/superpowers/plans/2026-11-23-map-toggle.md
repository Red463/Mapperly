# Character-specific map toggle correction

User report: M opens the map but the next M reopens instead of closing on another character. Native source inspection shows QuestLogOwnerMixin.HandleUserActionToggleSelf considers character map/quest display CVars and can request an open/maximized state while Mapperly keeps a windowed shell. Behavioral regression reproduces this mismatch before the fix. Wrap only the attached map instance toggle: visible closes via HideUIPanel; hidden delegates arguments/results to the native method. Keep the global ToggleWorldMap, bindings, opening restrictions, shared mixins and CVars untouched. Reuse the close helper for the header X. Verify all 16 native/Mapperly display combinations plus position/layout regressions and package rc.3. Live affected-character confirmation remains required.

Native reference: https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_WorldMap/QuestLogOwnerMixin.lua
