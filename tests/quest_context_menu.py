"""Native quest menu extension preserves defaults and validates captured targets."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/quest_navigation.py'))['lua']
l.execute('''
local callbacks={};local installs=0
Menu={ModifyMenu=function(tag,callback) installs=installs+1;callbacks[tag]=callback;return {} end}
TEST_MENU_CALLBACKS=callbacks
''')
l.execute('assert(loadstring(...))("Mapperly",A)',(root/'QuestContextMenu.lua').read_text())
l.execute('''
local M=A.QuestContextMenu
assert(M.Install() and M.Install());assert(TEST_MENU_CALLBACKS.MENU_QUEST_MAP_LOG_TITLE)
local active=true;local many=false;local calls=0
C_QuestLog={GetNumQuestLogEntries=function() return active and 1 or 0 end,GetInfo=function() return {questID=40,title='Test quest',level=10} end,IsComplete=function() return false end,
 GetQuestsOnMap=function(map) local p={{questID=40,x=.4,y=.5,mapID=map,inProgress=true}};if many then p[2]={questID=40,x=.6,y=.5,mapID=map,inProgress=true} end;return p end}
GetQuestUiMapID=function() return 1431 end
A.QuestLocationData=nil
A.Navigation={ToPin=function(p) calls=calls+1;assert(p.questID==40);return true end}
local function description()
 local d={items={},enabled=true}
 function d:CreateButton(label,callback) local c=description();c.label=label;c.callback=callback;table.insert(self.items,c);return c end
 function d:SetEnabled(v) self.enabled=v end
 function d:SetTooltip(fn) self.tooltip=fn end
 function d:CreateDivider() self.divider=true end
 function d:SetScrollMode(v) self.scroll=v end
 return d
end
local owner={questID=40};local root=description();root:CreateButton('Track');root:CreateButton('Abandon')
TEST_MENU_CALLBACKS.MENU_QUEST_MAP_LOG_TITLE(owner,root)
assert(#root.items==3 and root.items[1].label=='Track' and root.items[2].label=='Abandon')
local go=root.items[3];assert(go.label=='Navigate to' and go.callback)
owner.questID=99;go.callback();assert(calls==1,'recycled menu owner cannot change captured quest destination')
active=false;go.callback();assert(calls==1,'abandoned quest must not start stale menu navigation')
active=true;many=true;local sub=description();TEST_MENU_CALLBACKS.MENU_QUEST_MAP_LOG_TITLE({questID=40},sub)
local nav=sub.items[1];assert(nav.label=='Navigate to' and not nav.callback and #nav.items==2 and nav.scroll)
nav.items[2].callback();assert(calls==2)
C_QuestLog.GetQuestsOnMap=function() return {} end
local missing=description();TEST_MENU_CALLBACKS.MENU_QUEST_MAP_LOG_TITLE({questID=40},missing)
assert(#missing.items==1 and missing.items[1].enabled==false and missing.items[1].tooltip)
local waypoint=description();TEST_MENU_CALLBACKS.MENU_QUEST_MAP_LOG_TITLE({},waypoint);assert(#waypoint.items==0)
local bad=description();TEST_MENU_CALLBACKS.MENU_QUEST_MAP_LOG_TITLE({questID=0/0},bad);assert(#bad.items==0)
''')
# Late Menu loading must not need replacement hooks or duplicate callbacks.
l2=runpy.run_path(str(root/'tests/quest_navigation.py'))['lua']
l2.execute('Menu=nil')
l2.execute('assert(loadstring(...))("Mapperly",A)',(root/'QuestContextMenu.lua').read_text())
l2.execute('''
assert(not A.QuestContextMenu.Install());local n=0
Menu={ModifyMenu=function() n=n+1 end}
A.QuestContextMenu.driver:GetScript('OnEvent')(A.QuestContextMenu.driver,'ADDON_LOADED','Blizzard_Menu')
A.QuestContextMenu.driver:GetScript('OnEvent')(A.QuestContextMenu.driver,'PLAYER_LOGIN')
assert(n==1,'late loading must install exactly once')
''')
print('PASS: native menu preservation, single/multiple/unavailable locations, recycled owner/stale guards and late loading')
