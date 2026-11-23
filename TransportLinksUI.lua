local _,A=...
local L=A.TransportLinks
function L.Show(pin)
    local rows=L.ForPin(pin)
    if #rows==0 then return false end
    local f=L.window
    if not f then
        local U=A.Dialogs
        f=U.Window('MapperlyTransportLinksWindow','Travel connections','Choose a destination using your available travel methods.',640,510);L.window=f
        f.source=U.Label(f,'',24,88,'GameFontNormal');f.source:SetWidth(590)
        f.list=U.List(f,24,118,592,270)
        f.status=U.Label(f,'',24,414,'GameFontDisableSmall');f.status:SetSize(592,42);f.status:SetWordWrap(true)
        U.Action(f,'Close',504,460,112,function() f:Hide() end)
        f:HookScript('OnHide',function() if A.BoatLinks then A.BoatLinks.Clear() end end)
    end
    f.pin=pin;f.source:SetText(rows[1].fromName or pin.name or 'Transport')
    f.status:SetText(A.db.navigationMode=='direct' and 'Smart routing is off: navigation uses a straight line.' or 'The planner chooses enabled connections; boarding is manual. Overview links are schematic.')
    f.list:Render(rows,function(item,row)
        item.title:SetWidth(300);item.title:SetText(row.toName or row.name)
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
            item.preview=A.Dialogs.Action(item,'Preview',340,4,92,function() act(false) end)
            item.navigate=A.Dialogs.Action(item,'Navigate',438,4,92,function() act(true) end)
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
