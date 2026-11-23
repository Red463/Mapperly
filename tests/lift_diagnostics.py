"""Opt-in lift recorder captures raw evidence without changing route state."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'tools/diagnostics/LiftDiagnostics.lua').read_text(encoding='utf8'))
lua.execute('''
local D=A.LiftDiagnostics
assert(D.observer:IsShown() and D.observer:GetWidth()==1,'recording driver must remain active when the map is closed')
local saved=A.db;local target=A.Navigation.target;local active=A.Journey.active
local old=A.Journey.PlayerPosition
A.Journey.PlayerPosition=function() return {mapID=1413,x=.44,y=.92} end
UnitPosition=function() return -4620,-1840,42,1 end
GetTime=function() return 123 end
SlashCmdList.MAPPERLY('liftdiag start');assert(D.enabled)
for i=1,700 do D.Sample() end
assert(#D.lines==600,'recording must stay bounded')
local report=D.Report()
assert(report:find('-4620.000,-1840.000,42.000,1.000',1,true),'report must preserve actual native height and axes')
assert(report:find('map,x,y=1413.000,0.440,0.920',1,true))
UnitPosition=function() error('protected position') end
assert(pcall(D.Sample) and D.Report():find('<unavailable>',1,true),'unavailable position cannot break capture')
local count=#D.lines
SlashCmdList.MAPPERLY('liftdiag report')
assert(not D.enabled and D.window:IsShown() and D.edit:GetText():find('Mapperly lift diagnostics',1,true))
assert(MapperlyLiftDiagnosticsDB.report==D.edit:GetText(),'report must remain saved after logout')
D.observer:GetScript('OnUpdate')(D.observer,1)
assert(#D.lines==count,'viewing report must freeze capture')
assert(A.db==saved and A.Navigation.target==target and A.Journey.active==active,'capture cannot mutate navigation or settings')
A.Journey.PlayerPosition=old
''')
print('PASS: bounded read-only lift capture, guarded native positions, copyable report and persistence')
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'tools/diagnostics/LiftDiagnostics.lua').read_text(encoding='utf8'))
lua.execute('''
local saved=MapperlyLiftDiagnosticsDB.report
SlashCmdList.MAPPERLY('liftdiag report')
assert(MapperlyLiftDiagnosticsDB.report==saved and A.LiftDiagnostics.edit:GetText()==saved,'reload must retain and reopen the previous capture instead of overwriting it')
local J=A.Journey;local oldPlan,oldLeg,oldIndex,oldPosition=J.active,J.legIndex,J.index,J.PlayerPosition
local row=A.LocalTransportData.edges[1]
J.active={multiZone=true,points={row.a},legs={{kind='walk',mapID=row.a.mapID,first=1,last=1},{kind='transport',transport=row}}}
J.legIndex=1;J.index=1;J.PlayerPosition=function() return row.a end
SlashCmdList.MAPPERLY('liftdiag start')
local report=A.LiftDiagnostics.Report()
assert(report:find('legKind=walk',1,true) and report:find('servicePhase=upcoming',1,true),'capture must expose missed boarding-step transitions')
assert(report:find('exitCell=',1,true) and report:find('aimDistance=',1,true),'capture must explain the actual aim and exit-mask decision')
SlashCmdList.MAPPERLY('liftdiag stop')
J.active,J.legIndex,J.index,J.PlayerPosition=oldPlan,oldLeg,oldIndex,oldPosition
''')
