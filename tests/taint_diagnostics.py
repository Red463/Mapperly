"""Read-only diagnostic capture: bounded events, native error stacks and taint owners."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text())
lua.execute('''
fakeUI();A={version='test',map=WorldMapFrame};GetTime=function()return 12 end
local create=CreateFrame
CreateFrame=function(kind,...)
 local f=create(kind,...)
 if kind=='FontString' then f.GetStringWidth=function(self)return #self:GetText()*7 end end
 return f
end
InCombatLockdown=function()return true end
GetBuildInfo=function()return '1.60.1','71037','date',16001 end
UnitName=function()return 'PrivatePlayer' end;UnitGUID=function()return 'PrivateGUID' end
GetRealmName=function()return 'PrivateRealm' end
issecretvalue=function(v)return v=='SECRET' end
issecurevariable=function(t,k)if k=='expandedMapInsetsByMapID' then return false,'Mapperly' end;return true end
debugstack=function()return 'Blizzard_MapCanvas.lua:331 PrivatePlayer PrivateGUID PrivateRealm' end
hooksecurefunc=function()error('Diagnostic must not hook native execution')end
seterrorhandler=function()error('Diagnostic must not replace the error handler')end
ScriptErrorsFrame={GetErrorData=function(_,i)
 if i==1 then return {message='Unrelated error',stack='do not include'} end
 if i==2 then return {message="GetAuraDataByIndex(): tainted by Mapperly",stack='EditModeManager.lua:87 PrivatePlayer',count=1} end
 if i==3 then return {message='SECRET',stack='SECRET'} end
end}
SlashCmdList.MAPPERLY=function(msg)oldCommand=msg end
A.Print=function()end
''')
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'tools/diagnostics/TaintDiagnostics.lua').read_text())
for name in ['Buttons.lua','Dialogs.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
lua.execute('''
local D=A.TaintDiagnostics
D.events:GetScript('OnEvent')(D.events,'ADDON_LOADED','Mapperly')
local function event(addon,fn)D.events:GetScript('OnEvent')(D.events,'ADDON_ACTION_BLOCKED',addon,fn)end
event('OtherAddon','Other()');event('SECRET','SECRET')
assert(D.total==0,'Only readable Mapperly blocked actions belong in this capture')
event('Mapperly','Button:SetPassThroughButtons()')
local report=D.Build()
assert(report:find('Button:SetPassThroughButtons()',1,true) and report:find('Blizzard_MapCanvas.lua:331',1,true))
assert(report:find('EditModeManager.lua:87',1,true),'Preserve the full native warning stack')
assert(report:find('expandedMapInsetsByMapID: tainted by Mapperly',1,true))
assert(not report:find('PrivatePlayer',1,true) and not report:find('PrivateGUID',1,true) and not report:find('PrivateRealm',1,true))
assert(not report:find('SECRET',1,true) and not report:find('Unrelated error',1,true))
for i=1,100 do event('Mapperly','Button:SetPassThroughButtons()')end
assert(D.total==101 and #D.entries<=D.limit)
D.events:GetScript('OnEvent')(D.events,'PLAYER_LOGOUT')
assert(type(MapperlyTaintDiagnosticsDB.report)=='string')
local before=D.total;SlashCmdList.MAPPERLY('help');assert(oldCommand=='help' and D.total==before)
D.Open();assert(not D.frame,'Do not create the report window in combat')
InCombatLockdown=function()return false end
D.Open();local window=D.frame;assert(window:IsShown() and window.edit:GetText():find('Mapperly taint investigation',1,true))
window:Hide();D.Open(true);assert(D.frame==window and window.edit:GetText()==MapperlyTaintDiagnosticsDB.report)
ScriptErrorsFrame.GetErrorData=function()error('Unavailable')end
issecurevariable=function()error('Unavailable')end
assert(type(D.Build())=='string','Inaccessible diagnostics must not break reporting')
''')
print('PASS: bounded passive taint capture, native full stacks, owner checks, privacy and unavailable APIs')
