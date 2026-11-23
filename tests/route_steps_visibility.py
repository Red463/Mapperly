"""Default-on migration and closing the current panel are separate preferences."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/route_steps.py'))['lua']
lua.execute('''
local R,N,J=A.RouteSteps,A.Navigation,A.Journey
local old=A.InitStore({showRouteSteps=false})
assert(old.showRouteSteps,'legacy close-button disable must be restored once')
R.SetShown(false);assert(not A.InitStore(old).showRouteSteps,'a subsequent explicit disable must survive reload')
R.SetShown(true);J.Clear();N.pending=nil;N.target={name='First journey'}
R.Refresh();assert(R.window:IsShown() and R.window:GetFrameStrata()=='DIALOG','on-screen steps must remain above the world map')
R.close:GetScript('OnClick')();R.Refresh()
assert(A.db.showRouteSteps and not R.window:IsShown(),'close only dismisses the current panel')
N.target={name='Next journey'};R.Refresh();assert(R.window:IsShown(),'a new journey must restore the default-on panel')
assert(R.driver:IsShown(),'refresh driver must remain explicitly visible')
N.target={map=1431,x=.4,y=.5,name='Same destination'};J.Clear();R.Refresh();R.close:GetScript('OnClick')()
local request,tick,refresh=J.Request,N.Tick,A.RefreshPins;local complete
local library=LibStub;LibStub=function() return {GetWorldCoordinatesFromZone=function(_,x,y) return -x*1000,-y*1000,0 end} end
J.Request=function(_,done) complete=done;return true end;N.Tick=function() end;A.RefreshPins=function() end
assert(N.Start(1431,40,50,'Same destination',{mode='terrain',automatic=true}))
complete({kind='walking',mapID=1431,name='Same destination',distance=100,estimatedSeconds=20,coverage='complete',
 points={{mapID=1431,x=.3,y=.5},{mapID=1431,x=.4,y=.5}},legs={{kind='walk',name='Walk to destination'}}})
R.Refresh();assert(not R.window:IsShown(),'automatic replanning of the same destination must retain temporary dismissal')
J.Request=request;N.Tick=tick;A.RefreshPins=refresh;LibStub=library
''')
print('PASS: default-on migration, persistent explicit disable, temporary close and next-journey restoration')
