"""Hover Nijel's Point before this character has recorded any local departures."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(root / 'tests/journey_ui.py'))['lua']
for file in ['Data/Flights.lua', 'Flights.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)', (root / file).read_text(encoding='utf8'))
lua.execute("""
UnitGUID=function() return 'Player-FlightHover' end
UnitFactionGroup=function() return 'Alliance' end
UnitClass=function() return 'Mage','MAGE' end
local B,L=A.BoatLinks,A.TransportLinks
local c=A.Flights.Character()
c.nodes[37]=true
A.db.filters.flight=true
A.db.continentFilters.flight=true
A.db.showTransportLinks=false
A.db.useFlights=true
A.map.GetMapID=function() return 1414 end
local info=C_Map.GetMapInfo
C_Map.GetMapInfo=function(id) if id==1414 then return {mapType=2} end;return info(id) end
A.map:Show()
A.map:GetCanvas():SetSize(1000,600)
LibStub=function() return {GetZoneCoordinatesFromWorldInstance=function(_,x,y) return .5+x/30000,.5+y/30000 end} end
local pin={category='flight',flightNodeID=37,map=1414}
assert(#L.ForPin(pin)==0,'this character has no observed departure')
assert(B.Hover(pin),"Nijel's Point should preview its native departures")
assert(#L.ForHover(pin)==4,'all four direct native departures should appear')
for _,r in ipairs(L.ForHover(pin)) do
    assert(r.previewOnly and #A.Flights.Path(r)>3)
    assert(not L.Act(pin,r.id,true),'a map preview cannot start an unconfirmed flight')
end
assert(B.lines[1]:IsShown())
B.Clear(pin)
assert(not B.lines[1]:IsShown() and next(c.offers)==nil)
A.db.useFlights=false;assert(not B.Hover(pin));A.db.useFlights=true
A.db.continentFilters.flight=false;assert(not B.Hover(pin));A.db.continentFilters.flight=true
UnitFactionGroup=function() return 'Horde' end;assert(not B.Hover(pin))
""")
print("PASS: Nijel's Point hover geometry, discovery isolation, filters and faction")
