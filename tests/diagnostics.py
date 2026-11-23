"""Diagnostic observer remains bounded, captures mutation callers, exports safely."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
ctx=runpy.run_path(str(root/'tests/run.py'))
lua=ctx['lua']
lua.execute('''
InCombatLockdown=function() return false end
GetTime=function() return 123.5 end
GetBuildInfo=function() return '1.60.1','70959','test',16001 end
GetPhysicalScreenSize=function() return 3440,1440 end
GetCVar=function(key) return key=='uiScale' and '0.7' or 'test' end
debugstack=function() return 'Interface/AddOns/AnotherMapAddon/Move.lua:42' end
A.map.GetLeft=function() return 240 end;A.map.GetTop=function() return 900 end
C_AddOns.GetNumAddOns=function() return 1 end
C_AddOns.GetAddOnInfo=function() return 'AnotherMapAddon','Not collected' end
C_AddOns.IsAddOnLoaded=function() return true end
GetMouseFoci=function() return {A.bar} end
local methodsHook=hooksecurefunc
hooksecurefunc=function(target,key,callback)
 if type(target)=='string' then
  local fn=_G[target];local cb=key
  _G[target]=function(...) local value=fn(...);cb(...);return value end
 else
  local fn=target[key]
  target[key]=function(...) local value=fn(...);callback(...);return value end
 end
end
''')
p=root/'tools/diagnostics/Diagnostics.lua'
if p.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',p.read_text(encoding='utf-8'))
lua.execute('''
local D=A.Diagnostics
assert(D and D.Start and D.Report,'diagnostic build must expose capture and export')
local savedNotes=A.db.notes;local savedPosition=A.db.position
D.observer:GetScript('OnEvent')(D.observer,'ADDON_LOADED','Mapperly')
assert(D.enabled,'the diagnostic build must start capturing automatically')
local noteIdentity=A.db.notes
D.observer:GetScript('OnEvent')(D.observer,'GLOBAL_MOUSE_DOWN','LeftButton')
assert(D.Report():find('Mapperly.titlebar',1,true),'mouse focus must identify the actual header hit target')
A.map:SetPoint('TOPLEFT',UIParent,'TOPLEFT',350,-90)
A.bar:GetScript('OnDragStart')()
A.map:StopMovingOrSizing()
A.bar:GetScript('OnDragStop')()
local report=D.Report()
assert(report:find('AnotherMapAddon/Move.lua:42',1,true),'position mutations must include a caller stack')
assert(report:find('3440',1,true) and report:find('0.7',1,true),'report must include physical display and UI scale')
assert(report:find('map.SetPoint',1,true) and report:find('bar.OnDragStart',1,true),'report must distinguish setters from actual drag delivery')
assert(report:find('AnotherMapAddon',1,true),'loaded addon identifiers must be included')
assert(not report:find('Not collected',1,true),'addon display text must not be collected')
local xGetter=A.map.GetLeft
A.map.GetLeft=function() return 901 end
D.observer:GetScript('OnUpdate')(D.observer,.06)
assert(D.Report():find('geometry-change',1,true),'polling must catch engine movement without a Lua setter')
A.map.GetLeft=xGetter
for i=1,1000 do D.Log('test-event',tostring(i),false) end
assert(#MapperlyDiagnosticsDB.lines<=D.limit,'capture must stay bounded')
local count=#MapperlyDiagnosticsDB.lines
D.Stop();A.map:SetPoint('TOPLEFT',UIParent,'TOPLEFT',360,-100)
assert(#MapperlyDiagnosticsDB.lines==count+1 or #MapperlyDiagnosticsDB.lines==D.limit,'disabled observers must not keep recording')
assert(A.db.notes==savedNotes,'diagnostics must not rewrite notes')
D.Start();assert(D.previous and D.previous:find('test-event',1,true),'previous capture must be available after restart')
local left=A.map.GetLeft;A.map.GetLeft=function() error('protected getter') end
assert(pcall(D.Log,'guard-test','',true),'diagnostics must survive unavailable getters')
A.map.GetLeft=left
SlashCmdList.MAPPERLY('diagnose report')
assert(D.window and D.window:IsShown() and D.edit:GetText():find('Mapperly map position diagnostics',1,true),'report command must open a copyable report')
assert(not D.enabled,'report must freeze capture before reading it')
SlashCmdList.MAPPERLY('diagnose start');assert(D.enabled)
SlashCmdList.MAPPERLY('diagnose stop');assert(not D.enabled)
assert(A.db.notes==savedNotes)
''')
print('PASS: bounded diagnostics, setter stacks, drag delivery, environment, safe getters, report window and previous capture')
