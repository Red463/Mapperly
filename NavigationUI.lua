local _,A=...
function A.ShowNavigationInput(map)
    map=map or (A.map and A.map:GetMapID())
    if not map then A.Print('Open the destination map first.');return end
    if not A.navigationWindow then
        local f=CreateFrame('Frame','MapperlyNavigationWindow',UIParent,'BackdropTemplate');A.navigationWindow=f
        f:SetSize(360,260);f:SetPoint('CENTER');f:SetFrameStrata('DIALOG');f:SetClampedToScreen(true)
        f:SetBackdrop({bgFile='Interface\\Buttons\\WHITE8X8',edgeFile='Interface\\DialogFrame\\UI-DialogBox-Border',edgeSize=24,insets={left=6,right=6,top=6,bottom=6}})
        f:SetBackdropColor(.04,.045,.055,1)
        local function label(text,x,y,font)
            local t=f:CreateFontString(nil,'OVERLAY',font or 'GameFontHighlight')
            t:SetPoint('TOPLEFT',f,'TOPLEFT',x,-y);t:SetText(text);return t
        end
        label('Navigate to coordinates',24,22,'GameFontNormalLarge')
        f.zone=label('',24,54,'GameFontNormal');f.zone:SetWidth(310);f.zone:SetWordWrap(false)
        label('Enter X and Y from 0 to 100. Decimals are allowed.',24,80,'GameFontDisableSmall')
        local function input(text,x)
            label(text,x,107,'GameFontNormal')
            local e=CreateFrame('EditBox',nil,f,'InputBoxTemplate');e:SetSize(128,28);e:SetPoint('TOPLEFT',f,'TOPLEFT',x+4,-128)
            e:SetAutoFocus(false);e:SetMaxLetters(16)
            e:SetScript('OnEscapePressed',function() f:Hide() end)
            return e
        end
        f.xInput=input('X coordinate',24);f.yInput=input('Y coordinate',192)
        f.error=label('',24,172,'GameFontRedSmall');f.error:SetWidth(312);f.error:SetHeight(32);f.error:SetWordWrap(true)
        local function start()
            local ok,reason=A.Navigation.Start(f.targetMap,f.xInput:GetText(),f.yInput:GetText())
            if ok then f:Hide() else f.error:SetText(reason or 'Unable to start navigation.') end
        end
        f.xInput:SetScript('OnEnterPressed',start);f.yInput:SetScript('OnEnterPressed',start)
        f.xInput:SetScript('OnTabPressed',function() f.yInput:SetFocus() end)
        f.yInput:SetScript('OnTabPressed',function() f.xInput:SetFocus() end)
        f.start=A.CreateMapButton(f,'Start',72,24,start);f.start:ClearAllPoints();f.start:SetPoint('TOPLEFT',f,'TOPLEFT',24,-214)
        f.stop=A.CreateMapButton(f,'Stop',72,128,function() A.Navigation.Stop();f.error:SetText('Navigation stopped.') end)
        f.stop:ClearAllPoints();f.stop:SetPoint('TOPLEFT',f,'TOPLEFT',128,-214)
        local close=CreateFrame('Button',nil,f,'UIPanelCloseButton');close:SetPoint('TOPRIGHT',f,'TOPRIGHT',-4,-4);close:SetScript('OnClick',function() f:Hide() end)
        UISpecialFrames=UISpecialFrames or {};table.insert(UISpecialFrames,'MapperlyNavigationWindow')
    end
    local f=A.navigationWindow
    f.targetMap=map
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    f.zone:SetText(info and info.name or 'Map '..tostring(map));f.error:SetText('')
    local target=A.Navigation.target
    f.xInput:SetText(target and target.map==map and string.format('%.15g',target.x*100) or '')
    f.yInput:SetText(target and target.map==map and string.format('%.15g',target.y*100) or '')
    f:Show();f:Raise();f.xInput:SetFocus()
end
