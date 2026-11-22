# Mapperly themes

Choose **Default** or **Minimal Charcoal** in **Settings > Appearance theme**. The selector is available on both settings pages. Choices save immediately and apply to existing windows without a reload. Default follows Gatherly's Classic-style visual treatment but has no runtime Gatherly dependency. The internal saved identifier `gatherly` is retained for compatibility with earlier development builds.

Default uses native portrait/window chrome, warm opaque grey cards, cream text, gold headings, native tabs and red primary actions. Minimal Charcoal retains the charcoal palette, flat controls and unframed map. Changing themes preserves drafts, active tabs, navigation and other preferences.

`Theme.lua` owns the widget registry and guarded native-template helpers. Captions are drawn on the native skin frame so button and tab art cannot cover them. Inactive tab captions follow native text anchors. Minimal Charcoal restores inherited fonts, colours, shadows and native hover-label anchors.

The Default map has a 26-unit title bar with Mapperly and the installed version. The original crest uses full texture coordinates and an aligned circular mask. The standard Blizzard close button fits inside the title bar. Six-unit edge gutters keep the toolbar and footer clear of native trim, outside the 3:2 map viewport. The toolbar starts below the header. Toolbar and footer fills use a tiled native dialog/leather texture over a warm-brown base, independently of decorative borders. Idle icon faces blend into the material; hover and active feedback remain.

The fixed zone name and level range appear at the viewport's top centre in 18px white outlined text. The native area/POI hover label sits below it at a separate offset, retaining its content and priority behavior. Blizzard's Map Pin control is anchored to the upper-right of the viewport so the crest cannot cover it; native overlay adjustments reapply this position.

The quest pane retains native rows, difficulty colours and interactions. Default adds a warm-grey surface and hides only the native background texture's alpha; Minimal Charcoal restores it. Quest refresh/cropping hooks maintain the selected treatment and full-height background fitting.

Settings, destinations and notes use the same theme system and screen-fit scaling. Regression coverage includes saved choices, live switching with unsaved note content, late-created windows, template fallbacks, captions, tab spacing, native chrome, portrait cropping/masks, Minimal Charcoal restoration and map layout. Final rendering and addon-combination acceptance require in-game checks.
