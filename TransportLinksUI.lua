local _,A=...
local L=A.TransportLinks
function L.Show(pin)
    local rows=L.ForPin(pin)
    if #rows==0 then return false end
    local f=L.window
    if not f then
        local U=A.Dialogs
        f=U.ToolWindow('MapperlyTransportLinksWindow','Travel connections','Choose a destination',333,336);L.window=f
        f.source=U.Label(f,'',12,52,'GameFontNormal');f.source:SetWidth(310);f.source:SetWordWrap(false)
        f.list=U.List(f,10,76,313,186,{rowHeight=64,rowGap=3})
        f.status=U.Label(f,'',12,267,'GameFontDisableSmall');f.status:SetSize(309,31);f.status:SetWordWrap(true)
        U.Action(f,'Close',219,302,104,function() f:Hide() end)
        f:HookScript('OnHide',function() if A.BoatLinks then A.BoatLinks.Clear() end end)
    end
    f.pin=pin;f.source:SetText(rows[1].fromName or pin.name or 'Transport')
    f.status:SetText(A.db.navigationMode=='direct' and 'Smart routing is off: navigation uses a straight line.' or 'The planner chooses enabled connections; boarding is manual. Overview links are schematic.')
    f.list:Render(rows,function(item,row)
        item.title:SetText(row.toName or row.name)
        A.SetPinTexture(item.icon,row.kind=='flight' and 'flight' or 'transport',row.kind,24)
        local detail=L.methods[row.kind]..'  |  about '..math.max(1,math.ceil((row.planningSeconds or 60)/60))..' min'
        if row.kind=='flight' then detail=detail..'  |  '..A.Flights.Fare(row.fare,row.fareEstimated) end
        item.detail:SetText(detail)
        if not item.preview then
            local function act(navigate)
                local record=item.record;if not record then return end
                local ok,why=L.Act(f.pin,record.id,navigate)
                if ok then f:Hide() else f.status:SetText(why or 'Unable to plan this journey.') end
            end
            item.preview=A.Dialogs.Action(item,'Preview',8,33,131,function() act(false) end)
            item.navigate=A.Dialogs.Action(item,'Navigate',145,33,131,function() act(true) end)
            item:EnableMouse(true)
            item:SetScript('OnEnter',function() if item.record and A.BoatLinks then A.BoatLinks.Focus(f.pin,item.record.id) end end)
            item:SetScript('OnLeave',function() if A.BoatLinks then A.BoatLinks.Clear() end end)
            for _,button in ipairs({item.preview,item.navigate}) do
                button:HookScript('OnEnter',function() if item.record and A.BoatLinks then A.BoatLinks.Focus(f.pin,item.record.id) end end)
                button:HookScript('OnLeave',function() if A.BoatLinks then A.BoatLinks.Clear() end end)
            end
        end
    end)
    A.Dialogs.Show(f);return true
end
