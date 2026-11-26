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
assert(W.frame.rows and W.frame.rows[1].text:GetText():find('A shorter route',1,true),'show actual update highlights')
W.frame:Hide();assert(not W.TryShow(),'closing by X/Escape/Hide must not repeat')
A.version='1.2.0-test.1';assert(not W.TryShow(),'seen older versions should not repeat either')
-- Another modal delays display without consuming state.
A.version='1.2.0-test.3';A.ReleaseNotes={version=A.version,changes={'Improved controls.'}}
A.settingsWindow:Show();assert(not W.TryShow()and not W.Seen(A.version));A.settingsWindow:Hide()
for _,theme in ipairs({'gatherly','original'})do
 A.db.theme=theme;A.Theme.Apply()
 assert(W.TryShow());assert(W.frame:GetWidth()==520 and W.frame:GetHeight()<424,'short update notes should use a compact window')
 assert(W.frame.rows[1].text:GetWidth()<=464)
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
-- One to four wrapped highlights must fit above the footer/action with no
-- vertically centred content or large fixed-height gap.
local previousHeight=0
for count=1,4 do
 A.version='1.2.0-layout-'..count
 local lines={};for i=1,count do lines[i]=string.rep('A useful map improvement. ',6)end
 A.ReleaseNotes={version=A.version,changes=lines}
 assert(W.TryShow());local f=W.frame
 assert(f:GetHeight()>previousHeight,'window should follow release-note content')
 previousHeight=f:GetHeight()
 for i=1,count do
  local row=f.rows[i]
  assert(row:IsShown()and row.text:GetText()==lines[i],'all notes must remain visible')
  assert(-row.point[5]+row:GetHeight()<-f.hint.point[5],'rows must not overlap the footer')
 end
 assert(-f.done.point[5]+f.done:GetHeight()<=f:GetHeight()-12,'button must fit inside the frame')
 f:Hide()
end
A.version='1.2.0-paged'
local lines={};for i=1,9 do lines[i]='Entry '..i end
A.ReleaseNotes={version=A.version,changes=lines}
assert(W.TryShow())
local f=W.frame
assert(f.rows[1].text:GetText()=='Entry 1' and f.pageLabel:GetText()=='Page 1 of 3')
f.next:GetScript('OnClick')();assert(f.rows[4].text:GetText()=='Entry 8')
f.next:GetScript('OnClick')();assert(f.rows[1].text:GetText()=='Entry 9' and not f.rows[2]:IsShown())
f.previous:GetScript('OnClick')();assert(f.rows[1].text:GetText()=='Entry 5')
f:Hide();assert(not W.TryShow())
A.version='Unknown';assert(not W.TryShow(),'unavailable metadata must not create repeated unknown-version notices')
""")
print('PASS: welcome/update once per account/version, current notes, combat/world/modal deferral, corrupt state and both themes')
