"""Character recovery stores intent, never stale route indices or vehicle state."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/run.py'))['lua']
assert (root/'JourneySession.lua').exists(), 'journey session recovery module must exist'
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'JourneySession.lua').read_text())
lua.execute('''
local S,N,J=A.JourneySession,A.Navigation,A.Journey
UnitGUID=function() return 'Player-test' end
GetBuildInfo=function() return '1','123','date',11508 end
A.version='session-test'; A.db.rememberJourney=true
A.db.journeySessions=nil;S.Normalize(A.db)
N.target={map=1431,x=.4,y=.6,name='Intent |Hlink|h'};N.pending={map=1429,x=.1,y=.2,name='Pending'}
J.paused=true;J.active={};J.index=999;J.Leg=function() return {kind='walk'} end
assert(S.Capture());local row=A.db.journeySessions['Player-test']
assert(row.target.map==1431 and row.target.name=='Intent |Hlink|h' and row.paused and not row.index and not row.plan)
J.crossing=false;J.inStructure='owned-native-floor'
assert(S.Capture() and A.db.journeySessions['Player-test'].transit==true,'owned walking floor must require on-land confirmation even when crossing is false')
J.inStructure=nil;S.Capture()
N.target=nil;N.pending=nil;J.active=nil;J.paused=false
A.Flights.OnTaxi=function() return true end
S.OnWorldReady();S.Poll();assert(not S.frame or not S.frame:IsShown(),'taxi recovery waits for landing')
A.Flights.OnTaxi=function() return false end
A.Journey.PlayerPosition=function() return {mapID=1431,x=.2,y=.2} end
IsSwimming=function() return true end
S.Poll();assert(not S.frame or not S.frame:IsShown(),'swimming blocks the land recovery offer')
assert(not S.Resume(true),'swimming cannot confirm a land recovery')
local secret={};issecretvalue=function(v) return v==secret end
IsSwimming=function() return secret end
S.Poll();assert(not S.frame or not S.frame:IsShown(),'unreadable swimming status blocks recovery offer')
assert(not S.Resume(true),'unreadable swimming status cannot confirm land')
issecretvalue=nil;IsSwimming=function() return false end
S.Poll();assert(S.frame:IsShown(),'stable actual location offers recovery')
assert(S.frame.detail:GetText():find('Intent',1,true) and S.frame.detail:GetText():find('1431',1,true) and S.frame.detail:GetText():find('40.0, 60.0',1,true),'resume offer identifies saved destination and coordinates')
assert(S.frame.detail:GetText():find('||Hlink||h',1,true),'destination labels escape native hyperlink markup')
local requested;local start=N.Start
N.Start=function(map,x,y,name,options) requested={map=map,x=x,y=y,name=name,options=options};return true end
assert(S.Resume());assert(requested.map==1431 and requested.x==40 and requested.options.sessionResume)
N.target={map=1431,x=.4,y=.6,name='Intent'};J.active={};J.paused=false
S.Installed(N.target);assert(J.paused,'paused restore applies after install')
S.OnWorldReady();S.Intent();S.Poll();assert(not S.frame:IsShown(),'new intentional requests retire load offers')
S.Capture();local saved=A.db.journeySessions['Player-test'];saved.transit=true
N.target=nil;J.active=nil;S.OnWorldReady();S.Poll()
assert(not S.Resume(),'in-transit save requires explicit confirmation on land')
assert(S.Resume(true));S.Intent();J.paused=false;N.target={map=1431,x=.4,y=.6,name='Intent'};J.active={}
S.Installed(N.target);assert(not J.paused,'newer intent prevents stale pause callback')
N.Start=start;N.target=nil;J.active=nil
UnitGUID=function() return 'Player-other' end;S.OnWorldReady();S.Poll();assert(not S.frame:IsShown(),'character state must be isolated')
UnitGUID=function() return 'Player-test' end;A.version='incompatible';S.OnWorldReady();S.Poll();assert(not S.frame:IsShown(),'changed addon builds require a fresh route')
A.version='session-test';GetBuildInfo=function() return '1','456','date',11508 end
S.OnWorldReady();S.Poll();assert(not S.frame:IsShown(),'client patch build changes invalidate saved recovery')
GetBuildInfo=function() return '1','123','date',11508 end
UnitGUID=function() return nil end
S.events:GetScript('OnEvent')(S.events,'PLAYER_ENTERING_WORLD')
S.events:GetScript('OnUpdate')(S.events,2);assert(not S.frame:IsShown(),'login waits for readable character identity')
UnitGUID=function() return 'Player-test' end
J.PlayerPosition=function() return nil end
S.events:GetScript('OnUpdate')(S.events,2);S.Poll();assert(not S.frame:IsShown(),'login waits for actual position')
J.PlayerPosition=function() return {mapID=1431,x=.2,y=.2} end
S.Poll();assert(S.frame:IsShown(),'loading race eventually offers saved journey')
S.Intent();assert(S.Open(),'manual recovery offer uses the same validation')
S.Intent()
A.db.journeySessions['bad']={schema=1,build='bad',target={map=1431,x=0/0,y=.2}}
S.Normalize(A.db);assert(not A.db.journeySessions.bad,'corrupt state removed without deleting valid state')
for _,flag in ipairs({'paused','transit','manualFloor'}) do
 local corrupt={schema=saved.schema,build=saved.build,target=saved.target,profile=saved.profile};corrupt[flag]='true'
 A.db.journeySessions['bad-flag']=corrupt;S.Normalize(A.db)
 assert(not A.db.journeySessions['bad-flag'],'malformed '..flag..' must reject recovery rather than dropping its warning')
end
A.db.journeySessions['bad-walk']={schema=saved.schema,build=saved.build,target={map=1431,x=.4,y=.6,walkingOnly='true'}}
S.Normalize(A.db);assert(not A.db.journeySessions['bad-walk'],'malformed walkingOnly must reject recovery')
for i=1,30 do A.db.journeySessions['Player-'..i]=saved end
S.Normalize(A.db);local count=0;for _ in pairs(A.db.journeySessions) do count=count+1 end;assert(count<=8)
S.Clear();assert(not A.db.journeySessions['Player-test'])
A.db.rememberJourney=false;assert(not S.Capture())
''')
print('PASS: bounded character/build recovery, stable login, paused install, newer intent, taxi and explicit transit confirmation')

lua.execute('''
local S,N,J=A.JourneySession,A.Navigation,A.Journey
A.db.rememberJourney=true;A.db.journeySessions={}
N.target={map=1431,x=.4,y=.6,name='Same XY lift',recordedConnection='recorded-lift'}
J.Leg=function() return {kind='walk'} end;J.active={};J.paused=false;J.crossing=false;J.inStructure=nil
assert(S.Capture());local saved=A.db.journeySessions['Player-test']
assert(saved.manualFloor and saved.transit and not saved.target.recordedConnection,'forced same-XY recorded ride snapshots manual floor intent without restoring vehicle state')
N.target=nil;J.active=nil
local far,blocked,joinBlocked=false,false,false
A.TravelNetwork.Distance=function() return far and 100 or 0 end
A.TravelNetwork.World=function() return 600,400,0 end
A.Terrain.Segment=function(a,b) return not blocked and not (joinBlocked and a~=b) end
J.PlayerPosition=function() return {mapID=1431,x=.4,y=.6} end
local nativeInstance,nativeEast=0,600
UnitPosition=function() return 400,nativeEast,0,nativeInstance end
local accepted
N.Start=function(_,_,_,_,options) accepted=options;return true end
S.OnWorldReady();S.Poll()
assert(S.frame.detail:GetText():find('correct destination floor',1,true),'recorded floor recovery explains manual completion')
assert(not S.Resume(),'same-XY cannot establish floor without user confirmation')
nativeInstance=1;assert(not S.Resume(true),'wrong native instance blocks recorded floor recovery')
nativeInstance=0;nativeEast=620;assert(not S.Resume(true),'mismatched native XY blocks recorded floor recovery')
nativeEast=600;far=true;assert(not S.Resume(true),'far landing blocks recorded floor recovery')
far=false;blocked=true;assert(not S.Resume(true),'blocked current landing blocks recorded floor recovery')
blocked=false;joinBlocked=true;assert(not S.Resume(true),'blocked short join blocks recorded floor recovery')
joinBlocked=false;assert(S.Resume(true) and accepted.sessionResume and not accepted.recordedConnection,'explicit correct-floor confirmation replans without replaying old ride')
S.Intent();N.target={map=1431,x=.4,y=.6,name='Recorded leg'}
J.Leg=function() return {kind='transport',transport={recorded=true}} end
assert(S.Capture() and A.db.journeySessions['Player-test'].manualFloor,'active recorded transport retains manual-floor warning')
''')
print('PASS: recorded same-XY recovery requires explicit manual floor, native instance, proximity, dry landing and safe short join')
