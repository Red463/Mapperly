"""Exercise appearance controls and both render targets with reused regions."""
from pathlib import Path
import runpy

lua = runpy.run_path(str(Path(__file__).with_name('run.py')))['lua']
lua.execute("""
local S=A.RouteStyle
local U=A.Dialogs
local inputs,buttons={},{}
local input,action=U.Input,U.Action
U.Input=function(...)
    local field=input(...);inputs[#inputs+1]=field;return field
end
U.Action=function(parent,text,...)
    local button=action(parent,text,...);buttons[text]=button;return button
end
A.NavigationSettings.Build(CreateFrame('Frame'))
U.Input,U.Action=input,action
local function click(text) local b=buttons[text];b:GetScript('OnClick')(b) end
click('Route style')
assert(A.NavigationSettings.page=='style' and inputs[1]:GetText()=='#138F99')
local function enter(i,value)
    local field=inputs[i];field:SetText(value);field:GetScript('OnEnterPressed')(field)
end
enter(1,'#FA9602');enter(2,'AABBCC')
click('Width');click('Markers')
assert(S.Width()==4 and S.Shape()=='triangle')
for _,mini in ipairs({false,true}) do
    local parent=CreateFrame('Frame')
    local seg={{0,0,70,0,kind='ahead',base=parent:CreateLine()},
               {70,0,150,0,kind='completed',base=parent:CreateLine()}}
    local pool,fragments={},{}
    local options={anchor='CENTER',minimap=mini,worldUnit=not mini and 1 or nil,
        spacing=30,limit=2,size=5,strokeWidth=mini and 2.5 or 3}
    S.Render(seg,pool,fragments,parent,options)
    assert(seg[1].base.color[1]==250/255 and seg[2].base.color[3]==204/255)
    assert(math.abs(seg[1].base.thickness-options.strokeWidth*4/3)<.001)
    assert(pool[1][3]:IsShown() and pool[1].outline[3]:IsShown())
    click('Markers');S.Hide(pool);S.HideLines(fragments)
    S.Render(seg,pool,fragments,parent,options)
    assert(#seg[1].gaps==0 and not pool[1][3]:IsShown() and not pool[1][1]:IsShown())
    click('Markers');click('Markers')
end
A.InitStore(A.db)
assert(S.Shape()=='triangle' and S.Width()==4 and S.Color('routeAheadColor')[1]==250/255)
enter(1,'BADHEX');assert(S.Color('routeAheadColor')[1]==250/255)
click('Reset style')
assert(S.Width()==3 and S.Shape()=='chevron' and not A.db.routeAheadColor and not A.db.routeCompletedColor)
click('Back');assert(A.NavigationSettings.page=='display')
""")
print('PASS: route appearance controls, persistence, world/minimap rendering, marker cleanup and reset')
