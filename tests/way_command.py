"""Slash waypoint parsing and /way ownership across addon load orders."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
ctx=runpy.run_path(str(root/'tests/navigation.py'))
lua=ctx['lua']
lua.execute('''
A.InitStore({layoutVersion=2})
A.RefreshPins=function() end;A.UpdateButtonStates=function() end
A.AttachMap=function() end
C_Map.GetBestMapForUnit=function() return 1431 end
C_Map.GetMapInfo=function(id) return {mapID=id,name='Zone '..id} end
hbd.GetWorldCoordinatesFromZone=function(_,x,y,map) if map==999 then return end;return x*1000,y*1000,0 end
hbd.GetPlayerWorldPosition=function() return -100,-100,0 end
local create=CreateFrame
CreateFrame=function(...) local f=create(...);lastCreated=f;return f end
messages={};DEFAULT_CHAT_FRAME={AddMessage=function(_,s) messages[#messages+1]=s end}
hash_SlashCmdList={};hash_ChatTypeInfoList={}
''')
for file in ['Commands.lua','Core.lua']:
    p=root/file
    if p.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',p.read_text(encoding='utf-8-sig'))
lua.execute('''
local events=lastCreated:GetScript('OnEvent')
events(nil,'PLAYER_LOGIN')
assert(SLASH_MAPPERLYWAY1=='/way' and type(SlashCmdList.MAPPERLYWAY)=='function','unclaimed /way must register at login')
A.map:Hide()
SlashCmdList.MAPPERLYWAY('10.23 52.65')
assert(A.Navigation.target.map==1431 and math.abs(A.Navigation.target.x-.1023)<1e-10 and math.abs(A.Navigation.target.y-.5265)<1e-10,'closed map must use the player zone and retain decimal precision')
assert(#A.db.destinationHistory==1,'slash navigation must feed recent destinations')
A.map.GetMapID=function() return 1416 end;A.map:Show()
SlashCmdList.MAPPERLYWAY(' 25.5 75.25   Meeting point  ')
assert(A.Navigation.target.map==1416 and A.Navigation.target.name=='Meeting point','an open map supplies the destination zone and an optional name is preserved')
SlashCmdList.MAPPERLY('way 0 100 Edge')
assert(A.Navigation.target.x==0 and A.Navigation.target.y==1,'namespaced fallback must support coordinate boundaries')
local before=A.Navigation.target;local history=#A.db.destinationHistory
for _,bad in ipairs({'','10','bad 20','-1 20','101 50','10..23 52.65','1e999 50'}) do
 SlashCmdList.MAPPERLYWAY(bad)
 assert(A.Navigation.target==before and #A.db.destinationHistory==history,'invalid slash input must not replace the destination or change history')
end
A.map.GetMapID=function() return 999 end
SlashCmdList.MAPPERLYWAY('10 20');assert(A.Navigation.target==before,'unprojectable maps must report an error rather than silently use another zone')
A.map:Hide();C_Map.GetBestMapForUnit=function() return nil end
SlashCmdList.MAPPERLYWAY('10 20');assert(A.Navigation.target==before,'missing player map must preserve navigation')
C_Map.GetBestMapForUnit=function() return 1431 end
-- Another addon loaded before Mapperly must retain the command.
local otherCalls=0
local other=function(msg) otherCalls=otherCalls+1;assert(msg=='10 20') end
SLASH_OTHERWAY1='/WAY';SlashCmdList.OTHERWAY=other
hash_SlashCmdList['/WAY']=other;hash_ChatTypeInfoList['/WAY']='OTHERWAY'
events(nil,'ADDON_LOADED','OtherAddon')
assert(SLASH_MAPPERLYWAY1==nil and hash_SlashCmdList['/WAY']==other and SlashCmdList.OTHERWAY==other,'late-loaded addon must retain /way and its cache')
SlashCmdList.MAPPERLY('way 10 20')
assert(A.Navigation.target.map==1431,'namespaced fallback must still navigate when /way belongs to another addon')
-- A conflict discovered before registration must never be overwritten.
A.UpdateWayCommand()
assert(SLASH_MAPPERLYWAY1==nil and hash_SlashCmdList['/WAY']==other)
SLASH_OTHERWAY1=nil;SlashCmdList.OTHERWAY=nil
hash_SlashCmdList['/WAY']=nil;hash_ChatTypeInfoList['/WAY']=nil
A.UpdateWayCommand();assert(SLASH_MAPPERLYWAY1=='/way')
local ours=SlashCmdList.MAPPERLYWAY
hash_SlashCmdList['/WAY']=ours;hash_ChatTypeInfoList['/WAY']='MAPPERLYWAY'
-- Register an addon after login, before its pending alias has been cached.
SLASH_OTHERWAY1='/way';SlashCmdList.OTHERWAY=other
events(nil,'ADDON_LOADED','OtherAddon')
assert(SLASH_MAPPERLYWAY1==nil and hash_SlashCmdList['/WAY']==other and hash_ChatTypeInfoList['/WAY']=='OTHERWAY','relinquishing /way must replace only Mapperly-owned cached entries with the other owner')
assert(SlashCmdList.OTHERWAY==other and SLASH_OTHERWAY1=='/way')
-- Simulate Blizzard importing both handlers into its proxy and retaining our
-- cached alias. Yielding must restore the other cached handler for later uses.
local proxy={OTHERWAY=other,MAPPERLYWAY=ours}
SlashCmdList.OTHERWAY=nil;SlashCmdList.MAPPERLYWAY=nil
setmetatable(SlashCmdList,{__index=proxy})
hash_SlashCmdList['/WAY']=ours;hash_ChatTypeInfoList['/WAY']='MAPPERLYWAY'
ours('10 20')
assert(hash_SlashCmdList['/WAY']==other and hash_ChatTypeInfoList['/WAY']=='OTHERWAY','yielding an imported command must keep the other addon callable on subsequent uses')
hash_SlashCmdList['/WAY']('10 20')
assert(otherCalls==2)
-- Dynamic registration without ADDON_LOADED: stale cached handler must yield.

ours('10 20');assert(otherCalls==3,'stale Mapperly handler must delegate to the newly registered owner')
SLASH_OTHERWAY1=nil;SlashCmdList.OTHERWAY=nil
hash_SlashCmdList['/WAY']=other
A.UpdateWayCommand();assert(SLASH_MAPPERLYWAY1==nil,'cached-only owners must be respected')
hash_SlashCmdList['/WAY']=nil
IsSecureCmd=function(cmd) return cmd=='/WAY' end
A.UpdateWayCommand();assert(SLASH_MAPPERLYWAY1==nil,'native secure command ownership must be respected')
IsSecureCmd=nil
''')
print('PASS: /way precision, context, validation, history and namespaced fallback; existing, cached and late addon ownership preserved')
