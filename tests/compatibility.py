"""Warn about the active EQoL map mover without editing another addon's DB."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(r/'tests/run.py'))['lua']
l.execute('''
local C=A.Compatibility
assert(C and C.Check,'map mover conflict detection required')
InCombatLockdown=function()return false end
A.settingsWindow:Hide();A.navigationWindow:Hide()
if A.JourneySession.frame then A.JourneySession.frame:Hide()end
local db={enabled=true,frames={WorldMapFrame={enabled=true,x=123}}}
local entry={id='WorldMapFrame',defaultEnabled=true}
local api={GetEntryForFrameName=function(id)assert(id=='WorldMapFrame');return entry end,
 IsFrameEnabled=function()error('must not call mutating EQoL query')end}
EnhanceQoLMoverDB=db;EnhanceQoL=nil
assert(not C.Detect(),'stale saved variables alone must not warn')
EnhanceQoL={Mover={db=db,functions=api}}
assert(C.Detect(),'enabled mover and World Map should be detected')
db.enabled=false;assert(not C.Detect());db.enabled=true
db.frames.WorldMapFrame.enabled=false;assert(not C.Detect())
db.frames.WorldMapFrame.enabled=nil;assert(C.Detect(),'entry default should apply without initializing its DB')
assert(db.frames.WorldMapFrame.enabled==nil,'detection must not write defaults')
entry.defaultEnabled=false;assert(not C.Detect());entry.defaultEnabled=true
assert(not C.Check(),'wait for world entry')
C.events:GetScript('OnEvent')(C.events,'PLAYER_ENTERING_WORLD')
A.map:Hide();assert(not C.Check(),'wait for map opening')
A.map:Show()
InCombatLockdown=function()return true end;assert(not C.Check(),'defer in combat')
InCombatLockdown=function()return false end
A.settingsWindow:Show();assert(not C.Check(),'defer other Mapperly dialogs');A.settingsWindow:Hide()
assert(C.Check()and C.frame:IsShown())
assert(C.frame.body:GetText():find('World Map',1,true)and C.frame.body:GetText():find('/reload',1,true))
C.frame.done:GetScript('OnClick')(C.frame.done)
assert(not C.Check()and not C.frame:IsShown(),'do not repeat dismissed warning in the same session')
db.frames.WorldMapFrame.enabled=false;C.Check()
assert(not C.frame:IsShown(),'fixed configuration must not warn')
assert(db.enabled==true and db.frames.WorldMapFrame.x==123 and EnhanceQoLMoverDB==db,'preserve external settings')
api.GetEntryForFrameName=function()error('API unavailable')end
assert(not C.Detect(),'unknown entry without explicit enabled setting must not warn')
db.frames.WorldMapFrame.enabled=nil
assert(pcall(C.Detect),'changed or unavailable external API must be safe')
''')
print('PASS: read-only EQoL conflict detection, active flags/defaults, deferred warning and session dismissal')
