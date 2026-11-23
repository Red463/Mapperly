"""Flights preference, character discovery status and whole-fare preview labels."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
assert(A.flightsCheck and A.db.useFlights,'flight routing is default-on with its own preference')
A.Navigation.target=nil;A.Navigation.pending=nil;A.Journey.Clear()
A.flightsCheck:SetChecked(false);A.flightsCheck:GetScript('OnClick')(A.flightsCheck)
assert(A.db.useFlights==false)
A.NavigationSettings.Sync();assert(not A.flightsCheck:GetChecked())
A.flightsCheck:SetChecked(true);A.flightsCheck:GetScript('OnClick')(A.flightsCheck)
local row={kind='flight',fare=12345,fareEstimated=false}
A.JourneyView.Show({kind='walking',hasTransports=true,flightCost=12345,name='Flight test',distance=100,estimatedSeconds=120,coverage='complete',
 points={{mapID=1431,x=.1,y=.1},{mapID=1431,x=.2,y=.2}},legs={{kind='transport',transport=row,name='Flight: Offered destination'}}},
 {map=1431,x=.2,y=.2,name='Flight test'})
local text=A.JourneyView.steps:GetText()
assert(text:find('last quote 1g 23s 45c',1,true) and text:find('Flight total:',1,true))
assert(A.Flights.Fare(nil):find('unknown',1,true) and A.Flights.Fare(0):find('0c',1,true))
''')
print('PASS: saved flight preference, themed controls and whole-fare/unknown/free preview labels')
