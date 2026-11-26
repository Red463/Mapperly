"""Direction cue contrast, minimap cutouts and transport stippling."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/route_progress.py'))['lua']
lua.execute('''
local S=A.RouteStyle;local f=CreateFrame('Frame');local pool={}
local carry,used,gaps=S.Mark(pool,f,0,0,250,0,0,0,{spacing=100,limit=2,size=8,anchor='TOPLEFT',minimap=true,color={1,1,1,1}})
assert(gaps and #gaps==2,'each minimap direction cue reserves a gap in the stroke')
assert(pool[1].outline and pool[1].outline[1]:IsShown(),'markers need a dark outline')
assert(pool[1][1].color[1]>.9 and pool[1].outline[1].color[1]<.1,'arrow and outline must contrast strongly')
local faceLayer,faceLevel=pool[1][1]:GetDrawLayer()
local edgeLayer,edgeLevel=pool[1].outline[1]:GetDrawLayer()
assert(faceLayer==edgeLayer and faceLevel>edgeLevel,'cream chevrons must render explicitly above their dark outlines')
local pieces=S.Pieces(0,0,250,0,gaps)
assert(#pieces==3 and pieces[1][3]<100 and pieces[2][1]>100 and pieces[2][3]<200 and pieces[3][1]>200,'the minimap stroke must clear each reserved cue')
S.Hide(pool);assert(not pool[1][1]:IsShown() and not pool[1].outline[1]:IsShown(),'outlines must hide with their markers')
local segments={};local arrows,fragments={},{}
for i=1,25 do segments[i]={(i-1)*4,0,i*4,0,base=f:CreateLine(),kind='ahead'} end
local options={spacing=30,limit=2,size=8,anchor='TOPLEFT',strokeWidth=2,minimap=true}
S.Render(segments,arrows,fragments,f,options)
assert(#arrows==1 and arrows[1][1]:IsShown(),'the minimap keeps its nearest cue even with dense route vertices')
assert(not segments[6].base:IsShown() and segments[5].base.lineEnd[3]==20 and segments[9].base.lineStart[3]==32,'marker gaps must span dense neighbouring segments')
S.Hide(arrows);for _,line in ipairs(fragments) do line:Hide() end
segments[8].split=true;S.Render(segments,arrows,fragments,f,options)
assert(#segments[7].gaps==0,'minimap cue clearance cannot propagate across a route split')
-- Dense vertices must not restart the pattern at every point, or dashes
-- become one solid stripe and transport dots appear on top of each other.
local fine={}
local layer={}
for i=1,50 do fine[i]={i-1,0,i,0,base=f:CreateLine(),kind='transport'} end
options.minimap=false
S.Render(fine,{},layer,f,options)
assert(#layer.dots==5)
for i,dot in ipairs(layer.dots) do
 assert(dot:IsShown() and dot.point[4]==(i-1)*12)
 assert(dot.texture:find('RouteDot',1,true))
end
S.HideLines(layer)
for _,s in ipairs(fine) do s.kind='completed' end
options.minimap=true
S.Render(fine,{},layer,f,options)
assert(fine[1].base:IsShown() and not fine[8].base:IsShown() and fine[10].base:IsShown(),
 'travelled minimap dashes should carry their phase through short segments')
assert(not layer.dots[1]:IsShown())
local line=fine[1].base
assert(line.routeCasing.thickness>line.thickness and select(2,line.routeCasing:GetDrawLayer())<select(2,line:GetDrawLayer()))
S.HideLines({[0]=line})
assert(not line:IsShown() and not line.routeCasing:IsShown())
''')
print('PASS: contrasted direction markers, minimap cutouts, transport dots and pooled outline cleanup')
