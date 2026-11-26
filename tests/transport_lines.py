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
assert(not V.lines[3]:IsShown(),'transport must have open space between dots')
local count=0
for _,dot in ipairs(V.fragments.dots) do if dot:IsShown() then
 count=count+1;assert(dot.point[4]>=400 and dot.point[4]<=500 and dot.point[5]==-300,'dots must follow the native sailing piece')
end end
assert(count>1 and V.lines[1]:IsShown() and V.lines[1].routeCasing:IsShown())
''')
lua=runpy.run_path(str(root/'tests/minimap_route.py'))['lua']
lua.execute('''
radius=100;rotate='0';shape='SQUARE';heading=0
C_Minimap.GetViewRadius=function() return radius end
A.db.showMinimapRoute=true
local function p(x,ship,split) return {worldX=x,worldY=-500,instance=0,transport=ship,breakBefore=split} end
A.JourneyView.DisplayPlan=function() return {points={p(-560),p(-550),p(-440,true,true),p(-430,true)}} end
A.MinimapRoute.Update()
local shown=0;local dots=0
for _,line in ipairs(A.MinimapRoute.lines) do if line:IsShown() then shown=shown+1 end end
for _,dot in ipairs(A.MinimapRoute.fragments.dots) do if dot:IsShown() then
 dots=dots+1;assert(dot.point[4]<=-60 and dot.point[4]>=-70,'minimap dots must stay on their sailing piece')
end end
assert(shown==1 and dots>0,'minimap must preserve sailing splits and the dotted transport pattern')
''')
print('PASS: dotted sailing geometry and preserved manual handoffs on both maps')
