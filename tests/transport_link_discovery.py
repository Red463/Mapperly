"""Real observed-flight policy gates interactive connections and marker identity."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/flight_routes.py'))['lua']
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'TransportLinks.lua').read_text(encoding='utf8'))
lua.execute('''
local L=A.TransportLinks
A.db.filters.flight=true;A.db.continentFilters.flight=true
local pin={map=947,category='flight',flightNodeID=2}
assert(#L.ForPin(pin)==1 and L.ForPin(pin)[1].toNodeID==4,'only the observed outgoing offer may appear')
assert(L.IdentifyFlight(0,500,500)==2,'native world coordinates must bind the matching source master')
A.db.useFlights=false;assert(#L.ForPin(pin)==0);A.db.useFlights=true
GetMoney=function() return 0 end;assert(#L.ForPin(pin)==0,'known unaffordable flights must not bypass planner eligibility')
GetMoney=function() return 100 end;assert(#L.ForPin(pin)==1)
UnitGUID=function() return 'Player-Another' end
assert(#L.ForPin(pin)==0,'connections cannot reuse another character discovery')
''')
print('PASS: real flight discovery, fare eligibility, method preference and character isolation')
