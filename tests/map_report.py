"""Opt-in map movement diagnostics capture resets without changing layout."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/run.py'))['lua']
lua.execute('''
local R=A.MapReport
assert(R and R.Build and R.Start,'normal builds must include map reports')
assert(not R.enabled,'detailed capture must be opt-in')
InCombatLockdown=function()return false end
GetPhysicalScreenSize=function()return 3440,1440 end
GetCVar=function(k)return k=='uiScale'and '0.7'or 'test'end
GetBuildInfo=function()return '1.60.1','71037','test',16001 end
debugstack=function()return 'Interface/AddOns/AnotherMapAddon/Move.lua:42'end
UnitName=function()return 'PrivateName'end;UnitGUID=function()return 'Player-private-guid'end
GetRealmName=function()return 'PrivateRealm'end
C_AddOns.GetNumAddOns=function()return 1 end
C_AddOns.GetAddOnInfo=function()return 'AnotherMapAddon'end
C_AddOns.IsAddOnLoaded=function()return true end
local notes=A.db.notes;local position=A.db.position
local before=A.map.point
SlashCmdList.MAPPERLY('mapreport')
assert(R.frame:IsShown()and R.frame.edit:GetText():find('3440',1,true))
assert(R.frame.edit:GetText():find('uiScale=0.7',1,true))
assert(not R.enabled and A.map.point==before and A.db.position==position,'snapshot must not move or save the map')
R.frame:Hide()
SlashCmdList.MAPPERLY('mapreport start');assert(R.enabled)
GetMouseFoci=function()return {A.bar}end
R.observer:GetScript('OnEvent')(R.observer,'GLOBAL_MOUSE_DOWN','LeftButton')
assert(R.Build():find('focus=Mapperly.titlebar',1,true),'report must show which frame receives mouse input')
A.bar:GetScript('OnDragStart')()
A.map:SetPoint('TOPLEFT',UIParent,'TOPLEFT',240,-90)
A.bar:GetScript('OnDragStop')()
A.Theme.Set('original');A.Theme.Set('gatherly')
-- Simulate the symptom: a foreign setter resets the map after a settings change.
A.map:SetPoint('TOPLEFT',UIParent,'TOPLEFT',16,100)
local report=R.Build()
for _,s in ipairs({'map.SetPoint','bar.OnDragStart','Mapperly.ApplyLayout','AnotherMapAddon/Move.lua:42','largeSaved=','saved=','theme=gatherly','AnotherMapAddon'})do
 assert(report:find(s,1,true),'missing report evidence: '..s)
end
local left=A.map.GetLeft
A.map.GetLeft=function()return 987 end
R.observer:GetScript('OnUpdate')(R.observer,.15)
assert(R.Build():find('geometry-change',1,true),'capture engine changes without setters')
A.map.GetLeft=left
local secret={};issecretvalue=function(v)return v==secret end
local secretFrame=setmetatable({},{__index=function()error('protected frame access')end})
issecretvalue=function(v)return v==secret or v==secretFrame end
GetMouseFoci=function()return {secretFrame}end
assert(pcall(R.observer:GetScript('OnEvent'),R.observer,'GLOBAL_MOUSE_DOWN','LeftButton'),'secret mouse focus must not break observation')
A.map.GetLeft=function()return secret end
assert(pcall(R.Build),'secret geometry must not break reports')
A.map.GetLeft=function()error('protected getter')end
assert(pcall(R.Build),'unavailable geometry must not break reports')
A.map.GetLeft=left;issecretvalue=nil
R.Log('test','PrivateName Player-private-guid PrivateRealm |Hplayer:fake|h',true)
report=R.Build()
assert(not report:find('PrivateName',1,true)and not report:find('Player-private-guid',1,true)and not report:find('PrivateRealm',1,true)and not report:find('|',1,true))
for i=1,600 do R.Log('bounded-event',tostring(i),true)end
assert(#R.lines<=R.limit and #R.Build()<=R.maxBytes,'reports must remain bounded')
SlashCmdList.MAPPERLY('mapreport');assert(not R.enabled and R.frame:IsShown())
assert(R.frame.edit:GetText()==R.Build(),'copyable report should be frozen')
local n=R.total;A.map:SetPoint('TOPLEFT',UIParent,'TOPLEFT',50,-60)
assert(R.total==n,'capture must stop after export')
R.Start();R.Start();R.Log('single','',false)
assert(#R.lines<=R.limit,'restarting is safe')
local count=0
for _,line in ipairs(R.lines)do if line:find('capture-start',1,true)then count=count+1 end end
assert(count==1,'restart must clear earlier capture')
local function occurrences(s,part)local _,n=s:gsub(part,'');return n end
local old=occurrences(R.Build(),'map.SetPoint')
A.map:SetPoint('TOPLEFT',UIParent,'TOPLEFT',50,-70)
assert(occurrences(R.Build(),'map.SetPoint')==old+1,'restart must not install duplicate hooks')
SlashCmdList.MAPPERLY('mapreport stop');assert(not R.enabled)
assert(A.db.notes==notes,'diagnostics must not rewrite user notes')
''')
print('PASS: map snapshots, opt-in movement/settings trace, setter callers, bounded private-safe copyable export')
