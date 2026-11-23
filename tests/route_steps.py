"""On-screen journey steps remain a read-only view of navigation progress."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
local R=assert(A.RouteSteps,'on-screen route steps module must exist')
assert(A.db.showRouteSteps and A.routeStepsCheck)
local N,J=A.Navigation,A.Journey
N.pending=nil;N.target={map=1431,x=.8,y=.8,name='Final destination'}
local plan={multiZone=true,mapID=1431,points={{mapID=1431,x=.1,y=.1},{mapID=1431,x=.2,y=.2}},legs={
 {kind='walk',name='Walk through Duskwood'},
 {kind='transport',name='Flight: Stormwind to Ironforge',transport={kind='flight',toName='Ironforge'}},
 {kind='walk',name='Walk through Dun Morogh'},
 {kind='walk',name='Walk to the destination'},
 {kind='walk',name='Extra step'}}}
J.Install(plan);R.Refresh()
assert(R.window:IsShown() and R.current:GetText():find('Walk through Duskwood',1,true))
assert(R.rows[2]:GetText():find('Fly to Ironforge',1,true) and R.rows[5]:IsShown())
assert(R.destination:GetText():find('Final destination',1,true))
A.Theme.Set('original');assert(R.window.mapperlyThemeStyle=='original')
A.Theme.Set('gatherly');assert(R.window.mapperlyThemeStyle=='gatherly')
local index=J.index;R.Refresh();assert(J.index==index,'display must never mutate route progress')
J.legIndex=2;J.transportMessage='Flying to Ironforge';R.Refresh()
assert(R.current:GetText():find('Flying to Ironforge',1,true) and R.rows[3]:GetText():find('Dun Morogh',1,true))
assert(R.rows[2].highlight:IsShown() and not R.rows[1].highlight:IsShown(),'only current step should be highlighted')
A.Theme.Set(A.db.theme);R.Refresh()
assert(R.rows[2].textColor[1]==1 and R.rows[1].textColor[1]==.5,'theme reapplication must restore current/completed row colors')
J.paused=true;R.Refresh();assert(R.status:GetText():find('Paused',1,true))
J.paused=false;N.pending={name='New destination'};R.Refresh();assert(R.status:GetText():find('Updating',1,true))
R.collapse:GetScript('OnClick')();assert(A.db.routeStepsCollapsed and not R.current:IsShown())
assert(R.rows[1]:IsShown() and not R.rows[2]:IsShown(),'collapsed journey shows one current row')
R.collapse:GetScript('OnClick')();assert(not A.db.routeStepsCollapsed and R.rows[2]:IsShown())
assert(not R.upcoming:IsShown() and R.status:GetText()~='Drag to move','static route headings must be removed')
R.window:GetScript('OnDragStop')(R.window);assert(A.db.routeStepsAnchor and A.db.routeStepsAnchor.point=='CENTER')
R.close:GetScript('OnClick')();assert(A.db.showRouteSteps and not R.window:IsShown() and N.target,'closing panel cannot disable the saved option or stop navigation')
A.routeStepsCheck:SetChecked(true);A.routeStepsCheck:GetScript('OnClick')(A.routeStepsCheck);assert(A.db.showRouteSteps and R.window:IsShown())
N.pending=nil;J.Clear();R.Refresh();assert(R.current:GetText():find('Straight-line',1,true))
local width,height=UIParent:GetWidth(),UIParent:GetHeight()
UIParent:SetSize(340,160);R.Refresh();assert(R.window:GetHeight()*R.window.scale<=136.01,'panel must fit small screens')
UIParent:SetSize(width,height)
N.target=nil;N.pending={name='Pending destination'};R.Refresh();assert(R.current:GetText():find('Planning',1,true))
N.pending=nil;R.driver:GetScript('OnUpdate')(R.driver,.21);assert(not R.window:IsShown(),'refresh driver must hide completed navigation')
N.target={name='Long journey'};for i=6,14 do plan.legs[i]={kind='walk',name='Step '..i} end
J.Install(plan);J.legIndex=12;R.Refresh()
local visible,highlight=0,0
for _,row in ipairs(R.rows) do if row:IsShown() then visible=visible+1;if row.highlight:IsShown() then highlight=highlight+1;assert(row:GetText():find('12.',1,true)) end end end
assert(visible==10 and highlight==1,'long journeys must keep the current leg inside a ten-step window')
A.db.routeStepsAnchor={point='TOPLEFT',relativePoint='TOPLEFT',x=50,y=-100}
local saved=A.InitStore(A.db);assert(saved.routeStepsAnchor.x==50 and saved.routeStepsAnchor.y==-100)
A.InitStore({routeStepsAnchor={point='BAD',relativePoint='CENTER',x=0,y=0}});assert(not A.db.routeStepsAnchor)
A.InitStore({routeStepsAnchor={point='CENTER',relativePoint='CENTER',x=0/0,y=0}});assert(not A.db.routeStepsAnchor)
''')
print('PASS: route steps, progress/status, direct/planning modes, read-only behavior, visibility, collapse and anchor persistence')
