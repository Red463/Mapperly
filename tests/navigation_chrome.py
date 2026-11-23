"""Small navigation windows use native dialog materials and contained controls."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/planning_status.py'))['lua']
lua.execute('''
A.Theme.Set('gatherly');A.RouteSteps.Build()
for _,f in ipairs({A.PlanningStatus.frame,A.RouteSteps.window}) do
 assert(f.themeChrome and f.themeChrome:IsShown() and f.themeChrome.mapperlyNoPortrait and not f.themeChrome.themePortrait,'navigation panels must use matching native frame art without a crest')
 assert(f.compactFill and f.compactFill:IsShown() and f.compactFill.color[4]==1,'panel body must be opaque')
end
assert(A.PlanningStatus.frame.action.themeButtonRole=='primary','Cancel/Dismiss should use Blizzard button art')
assert(A.RouteSteps.collapse:GetHeight()<=24,'collapse control must fit within its title bar')
local N=A.Navigation;N.target={map=1431,x=.5,y=.5,name='Caption test'};N.pending=nil
A.RouteSteps.Refresh();A.RouteSteps.collapse:GetScript('OnClick')()
assert(A.RouteSteps.collapse.normalTexture=='Interface\\\\Buttons\\\\UI-PlusButton-Up','collapse must use the native plus icon immediately')
A.PlanningStatus.Failed(nil,{name='Failure'},'No route')
assert(A.PlanningStatus.frame.action.themeNativeButton.mapperlyCaption:GetText()=='Dismiss','visible action label must update without hovering')
A.Theme.Set('original')
assert(not A.RouteSteps.window.themeChrome:IsShown() and not A.RouteSteps.window.compactFill:IsShown() and A.RouteSteps.window.mapperlyThemeStyle=='original')
A.Theme.Set('gatherly');assert(A.RouteSteps.window.themeChrome:IsShown())
''')
print('PASS: native navigation dialog frames, title bars, controls and reversible theme switching')
