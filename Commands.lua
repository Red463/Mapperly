local _,A=...
local key='MAPPERLYWAY'
local alias='SLASH_'..key..'1'
local wayHandler
local function aliasHandler(globalName)
    local stem=globalName:sub(7)
    -- Try each numeric suffix: addon command identifiers may end in digits too.
    for split=#stem-1,1,-1 do
        if stem:sub(split+1):match('^%d+$') then
            local owner=stem:sub(1,split)
            local handler=SlashCmdList[owner]
            if type(handler)=='function' and handler~=wayHandler then return handler,owner end
        end
    end
end
local function wayOwner()
    if IsSecureCmd and IsSecureCmd('/WAY') then return true end
    -- Include aliases already imported into SlashCmdList's proxy, as well as
    -- new registrations not imported into the chat command cache yet.
    for name,value in pairs(_G) do
        if type(name)=='string' and name~=alias and name:match('^SLASH_.+%d$') and type(value)=='string' and value:lower()=='/way' then
            local handler,owner=aliasHandler(name)
            return true,handler,owner
        end
    end
    local cached=hash_SlashCmdList and hash_SlashCmdList['/WAY']
    if cached and cached~=wayHandler then return true,cached end
    local owner=hash_ChatTypeInfoList and hash_ChatTypeInfoList['/WAY']
    if owner and owner~=key then return true end
    return false
end
local function releaseWay(handler,owner)
    if _G[alias]=='/way' then _G[alias]=nil end
    if SlashCmdList[key]==wayHandler then SlashCmdList[key]=nil end
    if hash_SlashCmdList and hash_SlashCmdList['/WAY']==wayHandler then hash_SlashCmdList['/WAY']=handler end
    if hash_ChatTypeInfoList and hash_ChatTypeInfoList['/WAY']==key then hash_ChatTypeInfoList['/WAY']=owner end
end
function A.NavigateCommand(message)
    if not A.db then A.Print('Mapperly is still loading. Try again shortly.');return end
    local x,y,name=(message or ''):match('^%s*(%S+)%s+(%S+)%s*(.-)%s*$')
    if not x or not A.Navigation.Parse(x,y) then
        A.Print('Usage: /way X Y [name] or /mapperly way X Y [name]. Coordinates must be between 0 and 100.');return
    end
    local map
    if A.map and A.map:IsShown() then map=A.map:GetMapID()
    elseif C_Map and C_Map.GetBestMapForUnit then map=C_Map.GetBestMapForUnit('player') end
    local ok,reason=A.Navigation.Start(map,x,y,name)
    if not ok then A.Print(reason);return end
    local target=A.Navigation.target
    if target then A.Print(string.format('Navigating to %s: %s (%.2f, %.2f).',target.zone,target.name,target.x*100,target.y*100)) end
    return true
end
wayHandler=function(message,editBox)
    -- Also yield if another addon registers dynamically after ADDON_LOADED.
    local claimed,handler,owner=wayOwner()
    if claimed then
        releaseWay(handler,owner)
        if type(handler)=='function' then return handler(message,editBox) end
        A.Print('Use /mapperly way X Y for Mapperly navigation; /way has another owner.');return
    end
    return A.NavigateCommand(message)
end
function A.UpdateWayCommand()
    if not A.wayCommandsReady then return end
    local claimed,handler,owner=wayOwner()
    if claimed then releaseWay(handler,owner);return end
    if _G[alias]~='/way' or SlashCmdList[key]~=wayHandler then
        _G[alias]='/way';SlashCmdList[key]=wayHandler
    end
end
