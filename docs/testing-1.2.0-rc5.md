# Mapperly1.2.0-rc.5: simple tram test

Install the Mapperly folder from Mapperly-1.2.0-rc.5.zip and reload. No trip recording or station setup is required.

1. Enable Smart routing and Trams in Navigation settings. Temporarily disable flights if they would win the route comparison.
2. From Stormwind, choose a destination on the Ironforge map. The first tram instruction should be **Walk through the Stormwind tram portal**. Follow the city streets to its marker.
3. Enter the station. The instruction should change to **Ride the tram and exit the Ironforge portal**. Ride normally and leave through that portal.
4. On emerging into Ironforge, walking guidance should resume automatically. You do not need to stand on an exact exit marker, match a height, or click Continue on foot.
5. Repeat in reverse: **Walk through the Ironforge tram portal**, **Ride the tram and exit the Stormwind portal**, then resume walking. Try a Stormwind destination beyond the station area and replan once after exiting; it must not send you back on another tram round trip.
6. Try pause/resume during the city approach and leave/re-enter the source portal. Loading screens should retain the trip; exiting into the wrong city must not finish it.

Where indoor terrain masks cannot provide a route, city tram access uses a labeled direction to the portal or onward city marker. Follow the streets; the straight bearing is not a claim that you can walk through buildings. Ordinary routes, nearest-service walking searches and certified dock floors retain their existing rules.

Restore your normal flight/travel preferences afterward. If a stage sticks, send `/mapperly report` with the source city, destination, and whether you were outside, inside the station, or back in a city.
