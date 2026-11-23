local _,A=...
local W={windows={},worldReady=false};A.Announcements=W
local waiting,elapsed=false,0
local function version(v)
 return type(v)=='string' and v~='Unknown' and #v<=64 and v:match('^[%w][%w%.%_%-]*$') and v or nil
end
local function state()
 local db=A.db;if not db then return end
 local old=type(db.announcementState)=='table' and db.announcementState or {}
 local list,seen={},{}
 if type(old.versions)=='table' then
  for _,v in ipairs(A.ArrayValues(old.versions)) do
   v=version(v)
   if v and not seen[v] then list[#list+1]=v;seen[v]=true end
  end
 end
 while #list>128 do table.remove(list,1) end
 local result={welcomeSeen=old.welcomeSeen==true,versions=list}
 db.announcementState=result;return result
end
function W.Initialize(existingInstall)
 local alreadyInitialized=A.db and type(A.db.announcementState)=='table'
 local s=state()
 -- Old installs predate announcement tracking. They get update notes once;
 -- fresh installs persist the pending welcome even if display is deferred.
 if s and not alreadyInitialized and existingInstall then s.welcomeSeen=true end
end
function W.Seen(v)
 local s=state();if not s then return false end
 for _,saved in ipairs(s.versions) do if saved==v then return true end end
 return false
end
local function pending()
 local v=version(A.version);if not v then return end
 local s=state();if not s then return end
 if not s.welcomeSeen then return 'welcome',v end
 if not W.Seen(v) then return 'update',v end
end
local function mark(v)
 local s=state();s.welcomeSeen=true
 for _,saved in ipairs(s.versions) do if saved==v then return end end
 s.versions[#s.versions+1]=v
 while #s.versions>128 do table.remove(s.versions,1) end
end
local welcome=table.concat({
 '|cffffd100Make the map yours|r\nSwitch between compact and enlarged maps. Choose your theme and visible map layers.',
 '|cffffd100Find useful places|r\nSee inns, mailboxes, flight masters and dungeons, or add your own notes.',
 '|cffffd100Find your way|r\nSet a destination for route guidance, search quests, and revisit saved or recent places.',
 '|cffffd100Use quick map actions|r\nAlt-right-click the map to navigate. Hover a toolbar icon to see what it does.'
},'\n\n')
local function changes(v)
 local data=A.ReleaseNotes;local list={}
 if data and data.version==v and type(data.changes)=='table' then
  for _,line in ipairs(data.changes) do
   if type(line)=='string' and #list<4 then list[#list+1]='- '..line:sub(1,180):gsub('|','||') end
  end
 end
 if #list==0 then return 'Mapperly has been updated. Your settings, notes and saved destinations are kept.' end
 return table.concat(list,'\n\n')
end
local function busy()
 if InCombatLockdown and InCombatLockdown() then return true end
 for _,f in pairs(W.windows) do if f:IsShown() then return true end end
 for _,key in ipairs({'settingsWindow','navigationWindow','noteWindow'}) do
  local f=A[key];if f and f:IsShown() then return true end
 end
 for _,module in ipairs({A.JourneySession or {},A.PlanningStatus or {},A.RouteReport or {},A.MapReport or {},A.JourneyView or {},A.TransportLinks or {}}) do
  local f=module.frame or module.window;if f and f:IsShown() then return true end
 end
 return false
end
function W.TryShow()
 if not W.worldReady or not A.db or not A.Dialogs or busy() then return false end
 local kind,v=pending()
 if not kind then waiting=false;return false end
 local f=W.windows[kind]
 if not f then
  local U=A.Dialogs
  local title=kind=='welcome' and 'Welcome to Mapperly!' or "What's new in Mapperly"
  f=U.Window(kind=='welcome' and 'MapperlyWelcomeWindow' or 'MapperlyUpdateWindow',title,'Version '..v,520,424)
  f:Hide();W.windows[kind]=f
  f.body=U.Label(f,'',28,112,'GameFontHighlightSmall');f.body:SetSize(464,218);f.body:SetWordWrap(true);f.body:SetJustifyH('LEFT')
  f.hint=U.Label(f,'',28,342,'GameFontDisableSmall');f.hint:SetSize(464,22);f.hint:SetWordWrap(true)
  f.done=U.Action(f,'Got it',380,376,112,function()f:Hide()end)
 end
 f.body:SetText(kind=='welcome' and welcome or changes(v))
 f.hint:SetText(kind=='welcome' and 'Press M to open the map. Use the cog button for Settings.' or 'Your settings, notes and saved destinations are kept.')
 A.Dialogs.Show(f)
 if not f:IsShown() then return false end
 mark(v);waiting=false;W.current=kind;W.frame=f
 return true
end
local events=CreateFrame('Frame',nil,UIParent);W.events=events
 events:SetSize(1,1);events:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);events:EnableMouse(false)
for _,event in ipairs({'PLAYER_ENTERING_WORLD','PLAYER_LEAVING_WORLD','PLAYER_REGEN_ENABLED'}) do events:RegisterEvent(event) end
events:SetScript('OnEvent',function(_,event)
 if event=='PLAYER_LEAVING_WORLD' then
  W.worldReady=false;waiting=false;elapsed=0
  for _,f in pairs(W.windows) do f:Hide() end
 elseif event=='PLAYER_ENTERING_WORLD' then W.worldReady=true;waiting=true;elapsed=0
 elseif waiting then elapsed=.75 end
end)
events:SetScript('OnUpdate',function(_,dt)
 if not waiting then return end
 elapsed=elapsed+dt;if elapsed<.75 then return end;elapsed=0
 W.TryShow()
end)
