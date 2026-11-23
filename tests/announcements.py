"""Welcome/update notices appear once per account/version after world entry."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute("""
assert(A.Announcements and A.Announcements.TryShow,'announcement lifecycle is required')
local W=A.Announcements
local combat=false
InCombatLockdown=function()return combat end
for _,key in ipairs({'settingsWindow','navigationWindow','noteWindow'})do if A[key]then A[key]:Hide()end end
if A.JourneySession.frame then A.JourneySession.frame:Hide()end
if A.PlanningStatus and A.PlanningStatus.frame then A.PlanningStatus.frame:Hide()end
A.version='1.2.0-test.1';A.ReleaseNotes={version=A.version,changes={'New map features.','Clearer navigation.'}}
local db=A.InitStore({})
assert(not W.TryShow(),'do not show before world entry')
W.events:GetScript('OnEvent')(W.events,'PLAYER_ENTERING_WORLD')
combat=true;W.events:GetScript('OnUpdate')(W.events,1)
assert(not db.announcementState or not db.announcementState.welcomeSeen,'combat must not consume the notice')
combat=false;W.events:GetScript('OnUpdate')(W.events,1)
assert(W.current=='welcome'and W.frame:IsShown(),'first launch must show welcome')
assert(W.frame.themeTitleLabel:GetText()=='Welcome to Mapperly!')
assert(db.announcementState.welcomeSeen and W.Seen(A.version),'display marks welcome and current version')
W.frame.done:GetScript('OnClick')(W.frame.done);assert(not W.frame:IsShown())
W.events:GetScript('OnEvent')(W.events,'PLAYER_ENTERING_WORLD');W.events:GetScript('OnUpdate')(W.events,1)
assert(not W.frame:IsShown(),'zoning/reload should not repeat it')
A.InitStore(db);UnitGUID=function()return 'Another-character'end
assert(not W.TryShow(),'another character shares the seen account state')
A.version='1.2.0-test.2';A.ReleaseNotes={version=A.version,changes={'A shorter route to your destination.'}}
assert(W.TryShow() and W.current=='update')
assert(W.frame.themeTitleLabel:GetText()=="What's new in Mapperly")
assert(W.frame.body:GetText():find('A shorter route',1,true),'show actual update highlights')
W.frame:Hide();assert(not W.TryShow(),'closing by X/Escape/Hide must not repeat')
A.version='1.2.0-test.1';assert(not W.TryShow(),'seen older versions should not repeat either')
-- Another modal delays display without consuming state.
A.version='1.2.0-test.3';A.ReleaseNotes={version=A.version,changes={'Improved controls.'}}
A.settingsWindow:Show();assert(not W.TryShow()and not W.Seen(A.version));A.settingsWindow:Hide()
for _,theme in ipairs({'gatherly','original'})do
 A.db.theme=theme;A.Theme.Apply()
 assert(W.TryShow());assert(W.frame:GetWidth()==520 and W.frame:GetHeight()==424)
 assert(W.frame.body:GetWidth()<=464)
 W.frame:Hide();A.version=A.version..'x';A.ReleaseNotes.version=A.version
end
A.InitStore({announcementState={welcomeSeen='bad',versions={false,{},'good','good'}}})
assert(W.TryShow()and W.current=='welcome','malformed state must recover without crashing')
W.frame:Hide()
A.version='1.2.0-note-modal';A.ReleaseNotes={version=A.version,changes={'Better notes.'}}
A.noteWindow=A.noteWindow or CreateFrame('Frame');A.noteWindow:Show()
assert(not W.TryShow()and not W.Seen(A.version),'an open note editor must delay announcements')
A.noteWindow:Hide();assert(W.TryShow());W.frame:Hide()
A.version='1.2.0-transport-modal'
A.TransportLinks.window=A.TransportLinks.window or CreateFrame('Frame');A.TransportLinks.window:Show()
assert(not W.TryShow()and not W.Seen(A.version),'travel connections must delay announcements')
A.TransportLinks.window:Hide();assert(W.TryShow());W.frame:Hide()
A.version='1.2.0-existing';A.ReleaseNotes={version=A.version,changes={'Existing installations receive update notes.'}}
A.InitStore({notes={}});assert(W.Initialize,'saved-variable lifecycle must distinguish an existing installation')
W.Initialize(true);assert(W.TryShow()and W.current=='update','existing users get changes rather than a new-user welcome')
W.frame:Hide()
local fresh=A.InitStore({});W.Initialize(false)
-- Logging out before the delayed welcome must not turn a new user into legacy.
A.InitStore(fresh);W.Initialize(true)
assert(W.TryShow()and W.current=='welcome','a deferred first welcome survives reload')
W.frame:Hide()
A.version='Unknown';assert(not W.TryShow(),'unavailable metadata must not create repeated unknown-version notices')
""")
print('PASS: welcome/update once per account/version, current notes, combat/world/modal deferral, corrupt state and both themes')
