# Settings layout

The map toolbar uses one panel width for quests, nearby services and Mapperly tools. Settings is designed at 333 by 320 UI units. Its controls use normal UI scale when docked. Opening a different tool keeps the map canvas the same size. On short viewports, the panel can scroll to keep every control accessible.

- **Display** groups theme and map controls under **General**. **Size & opacity** contains compact size, marker size, a live preview and the two opacity sliders.
- **Layers** shows all eight categories with their icons, zone visibility and continent visibility. Show all and Hide all act on the zone visibility column.
- **Navigation** has separate pages for routing preferences, display, travel methods and recovery tools.
- **Navigation → Display → Route style** previews the completed and upcoming segments together. Choose either colour with a swatch or enter its hex value and press Enter. Width and marker buttons cycle through the options. Reset style restores the original map colours and markers.

The marker preview uses the four map textures for inns, mailboxes, dungeons and flight masters. The slider updates the icons at their actual selected size, including the texture variant used for map markers. The compact size slider ranges from 50 to 110 percent. At the lower end the shell reserves space for the toolbar and forms, subject to the available screen dimensions.

Automated checks cover panel and canvas dimensions, settings persistence, theme changes, live marker sizes, and restoring standalone editors after closing the drawer.
