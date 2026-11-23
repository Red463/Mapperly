"""Direction markers have a separated line gap and a high-contrast outline."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/route_progress.py'))['lua']
lua.execute('''
local S=A.RouteStyle;local f=CreateFrame('Frame');local pool={}
local carry,used,gaps=S.Mark(pool,f,0,0,250,0,0,0,{spacing=100,limit=2,size=8,anchor='TOPLEFT',color={1,1,1,1}})
assert(gaps and #gaps==2,'each direction marker needs an actual gap in the route stroke')
assert(pool[1].outline and pool[1].outline[1]:IsShown(),'markers need a dark outline')
assert(pool[1][1].color[1]>.9 and pool[1].outline[1].color[1]<.1,'arrow and outline must contrast strongly')
local faceLayer,faceLevel=pool[1][1]:GetDrawLayer()
local edgeLayer,edgeLevel=pool[1].outline[1]:GetDrawLayer()
assert(faceLayer==edgeLayer and faceLevel>edgeLevel,'cream chevrons must render explicitly above their dark outlines')
local pieces=S.Pieces(0,0,250,0,gaps)
assert(#pieces==3 and pieces[1][3]<100 and pieces[2][1]>100 and pieces[2][3]<200 and pieces[3][1]>200,'route strokes must not run beneath markers')
S.Hide(pool);assert(not pool[1][1]:IsShown() and not pool[1].outline[1]:IsShown(),'outlines must hide with their markers')
local segments={};local arrows,fragments={},{}
for i=1,25 do segments[i]={(i-1)*4,0,i*4,0,base=f:CreateLine(),color={1,.77,.18,.9},markable=true} end
local options={spacing=30,limit=2,size=8,anchor='TOPLEFT',strokeWidth=2}
S.Render(segments,arrows,fragments,f,options)
assert(#arrows==2,'dense route vertices must not make direction markers disappear')
assert(not segments[6].base:IsShown() and segments[5].base.lineEnd[3]==19 and segments[9].base.lineStart[3]==33,'marker gaps must span dense neighbouring segments')
S.Hide(arrows);for _,line in ipairs(fragments) do line:Hide() end
segments[8].split=true;S.Render(segments,arrows,fragments,f,options)
assert(#segments[7].gaps==0,'gaps cannot propagate across a route split')
''')
print('PASS: contrasted direction markers, true stroke gaps and pooled outline cleanup')
