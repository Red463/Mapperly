"""Remaining navigation controls must be themed, functional and unclipped."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute("""
A.Navigation.Stop();A.InitStore({})
assert(A.db.allowSwimming==true and A.db.rememberJourney==true,'new policy defaults preserve swimming and remember destinations')
A.settingsTabs.navigation:GetScript('OnClick')()
local S=A.NavigationSettings
assert(S.tabs and S.tabs.routing and S.tabs.travel and S.tabs.tools,'navigation choices should keep the added settings organized')
S.Select('routing')
assert(S.pages.routing:IsShown() and not S.pages.travel:IsShown() and A.swimmingCheck)
A.swimmingCheck:SetChecked(false);A.swimmingCheck:GetScript('OnClick')(A.swimmingCheck)
assert(A.db.avoidSwimming==false and A.db.allowSwimming==true)
A.swimmingCheck:SetChecked(true);A.swimmingCheck:GetScript('OnClick')(A.swimmingCheck);assert(A.db.avoidSwimming and A.db.allowSwimming)
S.Select('tools');assert(S.pages.tools:IsShown() and not S.pages.routing:IsShown() and A.rememberJourneyCheck)
local opened,forgot=0,0
local session,report=A.JourneySession,A.RouteReport
A.JourneySession={Open=function()opened=opened+1;return true end,Clear=function()forgot=forgot+1 end}
A.RouteReport={Open=function()opened=opened+1 end}
S.resumeButton:GetScript('OnClick')(S.resumeButton);S.reportButton:GetScript('OnClick')(S.reportButton)
assert(opened==2 and not S.connectionsButton and not A.RecordedTransports)
A.rememberJourneyCheck:SetChecked(false);A.rememberJourneyCheck:GetScript('OnClick')(A.rememberJourneyCheck);assert(not A.db.rememberJourney and forgot==1)
S.forgetButton:GetScript('OnClick')(S.forgetButton);assert(forgot==2)
SlashCmdList.MAPPERLY('report');SlashCmdList.MAPPERLY('connections');SlashCmdList.MAPPERLY('resume');assert(opened==4,'report/resume entry points remain; connections must not open a recorder')
for _,theme in ipairs({'gatherly','original'}) do
 A.db.theme=theme;A.Theme.Apply()
 for key,b in pairs(S.tabs) do assert(b.point[4]+b:GetWidth()<=616,'navigation sub-tabs must fit the existing settings window') end
 for _,b in ipairs({S.resumeButton,S.forgetButton,S.reportButton}) do assert(b:GetWidth()>=120) end
end
A.JourneySession=session;A.RouteReport=report
""")
print('PASS: routing/travel/tools layout, swimming/recovery defaults and controls, functional utility buttons and slash commands in both themes')
