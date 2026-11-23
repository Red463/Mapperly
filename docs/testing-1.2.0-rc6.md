# Mapperly1.2.0-rc.6: Ironforge navigation check

Replace the Mapperly folder with the one from Mapperly-1.2.0-rc.6.zip and reload. Keep Smart routing enabled.

1. Stand at the Ironforge spot where routes previously failed. Alt-right-click a destination elsewhere in the city. The route should start rather than report that the start or destination is blocked.
2. Test both a nearby destination and a point across the city. Where indoor path data is unavailable, guidance points toward the destination; follow the walkways. The preview identifies this as city direction guidance.
3. Try a destination outside Ironforge, then a route from outside into the city. It should connect via the normal city entrance rather than treating the whole indoor starting area as impassable.
4. Pause/resume one city route and take a short detour around buildings. It should keep the destination without repeated recalculation or Return to route messages on a city-direction leg.
5. Repeat with Trams disabled. Local Ironforge navigation does not depend on using a tram.

The reported start **33.1534,65.3159**, with Prefer roads enabled at Firm, is covered against all four reported destinations:63.6913,25.2976;65.2174,23.9557;32.9060,72.7385;59.9129,30.8279.

Optional native regression coordinates: Ironforge24.9,75.3 or60,40 to55.5,47.8 reproduce the former rejected-start condition in the bundled mask. Normal permitted paths such as18.7,51.5 to55.5,47.8 should still use ordinary terrain routing.

Outdoor routing and terrain permissions remain unchanged. Walking-only nearest-service searches retain their conservative reachable-path requirements; city direction bearings are not presented as verified shortest walking routes.

If the original failure persists, send `/mapperly report` immediately after the failed attempt, plus your player coordinates and the destination. This patch addresses the reproduced indoor-mask rejection; a different error may need a separate fix.
