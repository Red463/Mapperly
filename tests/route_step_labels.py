"""Route rows use concise method labels, icons, padding and detailed hover help."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/route_steps.py'))['lua']
lua.execute('''
local R,J,N=A.RouteSteps,A.Journey,A.Navigation
A.InitStore({});N.pending=nil;N.target={name='Goldshire'}
local plan={multiZone=true,mapID=1431,points={{mapID=1431,x=.1,y=.1},{mapID=1431,x=.2,y=.2}},legs={
 {kind='walk',name='Walk through Hillsbrad Foothills'},
 {kind='transport',transport={kind='flight',toName='Stormwind, Elwynn'},name='Flight: Southshore to Stormwind'},
 {kind='transport',transport={kind='boat',toName='Menethil Harbor'},name='Boat: Harbor'},
 {kind='transport',transport={kind='zeppelin',toName='Orgrimmar'},name='Zeppelin: Orgrimmar'},
 {kind='transport',transport={kind='airship',toName='Zephras'},name='Airship: Zephras'}}}
J.Install(plan);J.legIndex=2;J.transportMessage='Speak to the flight master; choose Stormwind in the flight window.';R.Refresh()
assert(R.rows[2]:GetText()=='2. Fly to Stormwind','active row must use the concise destination label')
assert(R.rows[3]:GetText()=='3. Boat to Menethil Harbor')
assert(R.rows[4]:GetText()=='4. Zeppelin to Orgrimmar' and R.rows[5]:GetText()=='5. Airship to Zephras')
assert(R.rows[1].icon and R.rows[2].icon.texture:find('FlightMaster',1,true) and R.rows[3].icon.texture:find('Boat',1,true))
assert(R.rows[1].frame:GetWidth()==272 and R.rows[1].frame:GetHeight()>=28,'rows need comfortable inset and vertical padding')
local addLine=GameTooltip.AddLine;local detail
GameTooltip.AddLine=function(_,text) detail=text end
R.rows[2].frame:GetScript('OnEnter')(R.rows[2].frame)
GameTooltip.AddLine=addLine
assert(GameTooltip:IsShown(),'detailed flight instructions remain accessible on hover')
assert(detail==J.transportMessage,'hover must retain the actual current boarding instructions')
local start,stop=R.window:GetScript('OnDragStart'),R.window:GetScript('OnDragStop');local dragged,stopped=false,false
R.window:SetScript('OnDragStart',function(...) dragged=true;start(...) end)
R.window:SetScript('OnDragStop',function(...) stopped=true;stop(...) end)
R.rows[2].frame:GetScript('OnDragStart')();R.rows[2].frame:GetScript('OnDragStop')()
assert(dragged and stopped and J.legIndex==2,'hover rows must preserve panel dragging without changing route progress')
J.legIndex=1;J.crossing=true;R.Refresh()
assert(R.rows[1].frame.details=='Continue through the zone crossing','walking hover must retain current passage/crossing instructions')
J.crossing=false;J.legIndex=2;R.Refresh()
local expanded=R.window:GetHeight()
R.collapse:GetScript('OnClick')()
assert(R.rows[1].frame:IsShown() and R.rows[1]:GetText()=='2. Fly to Stormwind' and not R.rows[2].frame:IsShown(),'collapsed panel must show only the current step')
assert(not R.destination:IsShown() and not R.status:IsShown() and not R.upcoming:IsShown() and R.window:GetHeight()<expanded)
''')
print('PASS: concise travel labels, matching icons, inset rows and hover instructions')
