"""Completed geometry, sparse chevrons and previews use authoritative progress."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
local S=assert(A.RouteStyle,'shared route progress styling must exist')
local J,V=A.Journey,A.JourneyView
local plan={kind='walking',name='Progress test',mapID=1431,distance=400,estimatedSeconds=100,
 points={{mapID=1431,x=.1,y=.5},{mapID=1431,x=.3,y=.5},{mapID=1431,x=.5,y=.5},{mapID=1431,x=.9,y=.5}},legs={{kind='walk',name='Walk'}}}
J.Install(plan);J.index=3
assert(S.Completed(plan,1) and not S.Completed(plan,2),'the current target segment is still upcoming')
assert(not S.Completed({points=plan.points},1),'a separate preview must never inherit active progress')
A.map.GetMapID=function() return 1431 end
A.db.showJourneyRoute=true;V.Show(plan,{map=1431,x=.9,y=.5,name='Progress test'});V.Refresh()
assert(V.lines[1].color[4]<V.lines[2].color[4],'completed geometry must be visibly faded')
assert(V.directions and #V.directions>0,'remaining route must have direction chevrons')
local a,b,c,d=S.Chevron(20,0,1,0,5)
assert(a<20 and c<20 and b*d<0,'chevron wings must sit behind its forward tip')
local before=J.index;V.Refresh();assert(J.index==before,'rendering cannot advance navigation')
plan.points[4].breakBefore=true;V.Refresh()
for _,line in pairs(V.lines) do
 if line:IsShown() then assert(line.lineEnd[3]<=500,'progress styling cannot reconnect gaps') end
end
J.Clear();V.Show(plan,{map=1431,x=.9,y=.5,name='Preview'});V.Refresh();assert(V.lines[1].color[4]>.5,'nonactive preview stays unfaded')
J.Install(plan);J.index=2;A.map:Show();V.Show(plan,{map=1431,x=.9,y=.5,name='Active'})
J.index=3;V.progressDriver:GetScript('OnUpdate')(V.progressDriver,.21)
assert(V.lines[1].color[4]<.5,'world map must refresh as follower progress changes')
local pool={};local carry,used=S.Mark(pool,V.overlay,0,0,10000,0,0,0,{spacing=100,limit=2,size=5,color={1,1,1,.6},anchor='TOPLEFT'})
assert(used==2 and #pool==2,'direction marks must stay strictly capped')
local preview={kind='walking',name='Separate preview',mapID=1431,distance=400,estimatedSeconds=100,points=plan.points,legs=plan.legs}
V.Show(preview,{map=1431,x=.9,y=.5,name='Separate preview'})
local original=V.Refresh;local refreshes=0;V.Refresh=function(...) refreshes=refreshes+1;return original(...) end
for i=1,10 do V.progressDriver:GetScript('OnUpdate')(V.progressDriver,.21) end
assert(refreshes==0,'unchanged separate preview must not repeatedly redraw for an active journey')
V.Refresh=original
''')
lua=runpy.run_path(str(root/'tests/minimap_route.py'))['lua']
lua.execute('''
local R=A.MinimapRoute
radius=100;rotate='0';shape='ROUND';heading=0
C_Minimap.GetViewRadius=function() return radius end
A.db.showMinimapRoute=true
local plan={points={{worldX=-600,worldY=-500,instance=0},{worldX=-550,worldY=-500,instance=0},{worldX=-450,worldY=-500,instance=0},{worldX=-400,worldY=-500,instance=0}}}
A.Journey={active=plan,index=3,Leg=function() end}
A.JourneyView.DisplayPlan=function() return plan end
R.Update();assert(R.lines[2].color[4]<.5 and R.lines[3].color[4]>.5,'both halves of the active segment use shared route progress')
assert(#R.directions==1 and R.directions[1][1]:IsShown(),'one minimap chevron on the way ahead')
for _,pair in ipairs(R.directions) do for _,line in ipairs(pair) do if line:IsShown() then
 for _,p in ipairs({line.lineStart,line.lineEnd}) do
  local x,y=p[3],p[4];assert(x*x+y*y>=64,'direction wings cannot cover the player arrow')
  assert(R.Clip(x,y,x,y,Minimap:GetWidth(),Minimap:GetHeight(),'ROUND'),'direction wings must stay inside round minimap')
 end
end end end
''')
print('PASS: authoritative completion, preview isolation, chevron direction and preserved splits')
