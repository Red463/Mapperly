"""Native sailing pieces never join across manual handoffs or teleport gaps."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
local V=A.JourneyView
A.db.showJourneyRoute=true;A.map.GetMapID=function() return 1431 end
local function p(x,ship,split) return {mapID=1431,x=x,y=.5,transport=ship,breakBefore=split} end
V.Show({kind='walking',hasTransports=true,name='Sailing',points={p(.1),p(.2),p(.4,true,true),p(.5,true),p(.6,false,true),p(.7)},distance=100,estimatedSeconds=300,legs={}}, {map=1431,x=.7,y=.5,name='Sailing'})
V.Refresh()
assert((not V.lines[2] or not V.lines[2]:IsShown()) and (not V.lines[4] or not V.lines[4]:IsShown()),'manual boarding and arrival joins cannot be drawn as walking shortcuts')
assert(V.lines[3]:IsShown() and V.lines[3].color[3]>V.lines[3].color[1],'native sailing geometry must have a distinct blue colour')
assert(V.lines[1].color[1]>V.lines[1].color[3])
''')
lua=runpy.run_path(str(root/'tests/minimap_route.py'))['lua']
lua.execute('''
radius=100;rotate='0';shape='SQUARE';heading=0
C_Minimap.GetViewRadius=function() return radius end
A.db.showMinimapRoute=true
local function p(x,ship,split) return {worldX=x,worldY=-500,instance=0,transport=ship,breakBefore=split} end
A.JourneyView.DisplayPlan=function() return {points={p(-560),p(-550),p(-440,true,true),p(-430,true)}} end
A.MinimapRoute.Update()
local shown=0;local blue=false
for _,line in ipairs(A.MinimapRoute.lines) do if line:IsShown() then shown=shown+1;blue=blue or line.color[3]>line.color[1] end end
assert(shown==2 and blue,'minimap must preserve sailing splits and blue geometry')
''')
print('PASS: separate sailing colour and no manual/teleport shortcut lines on both maps')
