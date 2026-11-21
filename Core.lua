local _,A=...
function A.Print(s) DEFAULT_CHAT_FRAME:AddMessage('|cffffd100Mapperly:|r '..s) end
function A.NoteEditBox(dialog)
    return dialog.GetEditBox and dialog:GetEditBox() or dialog.editBox
end
local function acceptNote(dialog,data)
    local edit=A.NoteEditBox(dialog)
    if not data or not edit or not A.AddNote(data.map,data.x,data.y,edit:GetText()) then return true end
    A.db.filters.notes=true
    A.Refresh()
end
StaticPopupDialogs.MAPPERLY_NOTE={text='Name this map note',button1=ACCEPT,button2=CANCEL,hasEditBox=true,maxLetters=120,timeout=0,whileDead=true,hideOnEscape=true,preferredIndex=3,
    OnAccept=acceptNote,
    EditBoxOnEnterPressed=function(edit,data)
        local dialog=edit:GetParent()
        if not acceptNote(dialog,data or dialog.data) then dialog:Hide() end
    end,
    EditBoxOnEscapePressed=function(edit) edit:GetParent():Hide() end}
local events=CreateFrame('Frame')
for _,event in ipairs({'ADDON_LOADED','PLAYER_LOGIN','PLAYER_REGEN_ENABLED','DISPLAY_SIZE_CHANGED','UI_SCALE_CHANGED','MAIL_SHOW','TAXIMAP_OPENED','GOSSIP_SHOW','CONFIRM_BINDER','MAP_EXPLORATION_UPDATED'}) do events:RegisterEvent(event) end
events:SetScript('OnEvent',function(_,event,name)
    if event=='ADDON_LOADED' and name=='Mapperly' then MapperlyDB=A.InitStore(MapperlyDB) end
    if not A.db then return end
    if event=='PLAYER_LOGIN' or event=='ADDON_LOADED' then A.AttachMap()
    elseif event=='DISPLAY_SIZE_CHANGED' or event=='UI_SCALE_CHANGED' then if A.map then A.ApplyLayout() end
    elseif event=='PLAYER_REGEN_ENABLED' then if A.layoutPending and A.map then A.ApplyLayout() end
    elseif event=='MAIL_SHOW' then A.Observe('mail','Mailbox');A.Refresh()
    elseif event=='TAXIMAP_OPENED' then A.Observe('flight',UnitName('npc') or 'Flight master');A.Refresh()
    elseif event=='CONFIRM_BINDER' then A.Observe('inn',UnitName('npc') or 'Inn');A.Refresh()
    elseif event=='GOSSIP_SHOW' and C_GossipInfo and C_GossipInfo.GetOptions then
        for _,v in ipairs(C_GossipInfo.GetOptions() or {}) do
            local icon=v.iconFileID or v.icon
            if tonumber(icon)==132052 or tonumber(icon)==132624 or v.type=='binder' or (type(icon)=='string' and icon:lower():find('binder',1,true)) then A.Observe('inn',UnitName('npc') or 'Inn');A.Refresh();break end
        end
    elseif event=='MAP_EXPLORATION_UPDATED' then A.Refresh() end
end)
SLASH_MAPPERLY1='/mapperly'
SlashCmdList.MAPPERLY=function(msg)
    if not A.db then return end
    if msg=='debug' then
        A.Print('Build 1.0.0; map '..tostring(A.map and A.map:GetMapID())..'; registered pins '..#A.pinPool)
        for i,pin in ipairs(A.pinPool) do
            if i>10 then break end
            local p=pin.data
            A.Print(string.format('%s: %s (%.1f, %.1f), layer %d, shown %s',p.category,p.name,p.x*100,p.y*100,pin:GetFrameLevel(),tostring(pin:IsShown())))
        end
        return
    end
    local map,x,y,name=msg:match('^note%s+(%d+)%s+([%d%.]+)%s+([%d%.]+)%s+(.+)$')
    if map then
        if not tonumber(x) or not tonumber(y) then A.Print('Invalid coordinates.');return end
        if not A.AddNote(tonumber(map),tonumber(x)/100,tonumber(y)/100,name) then A.Print('Invalid note coordinates (use 0–100).') end;A.Refresh();return
    end
    local category,m,cx,cy,label=msg:match('^pin%s+(%w+)%s+(%d+)%s+([%d%.]+)%s+([%d%.]+)%s+(.+)$')
    if category then
        if not tonumber(cx) or not tonumber(cy) then A.Print('Invalid coordinates.');return end
        local allowed=false;for _,k in ipairs(A.categories) do if k==category then allowed=true end end
        local p={category=category,map=tonumber(m),x=tonumber(cx)/100,y=tonumber(cy)/100,name=label:sub(1,120)}
        if allowed and A.ValidPin(p) then table.insert(A.db.observed,p);A.Refresh() else A.Print('Invalid pin category or coordinates.') end;return
    end
    if msg=='help' then A.Print('/mapperly: open map; /mapperly note <mapID> <x%> <y%> <name>; /mapperly pin <mail|inn|dungeon|flight|transport|portal|border> <mapID> <x%> <y%> <name>');return end
    A.AttachMap()
    if not A.map then A.Print('Native world map is not loaded yet. Open it with M, then try again.');return end
    if not A.map:IsShown() then if ToggleWorldMap then ToggleWorldMap() else A.map:Show() end else ToggleDropDownMenu(1,nil,A.menu,A.bar,0,0) end
end
