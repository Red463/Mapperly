local _,A=...
local T={};A.Theme=T
local registry=setmetatable({},{__mode='k'})
local function object(v) return type(v)=='table' or type(v)=='userdata' end
local function modern() return not A.db or A.db.theme~='original' end
local originalWindow={bgFile='Interface\\Buttons\\WHITE8X8',edgeFile='Interface\\DialogFrame\\UI-DialogBox-Border',edgeSize=24,insets={left=6,right=6,top=6,bottom=6}}
function T.PositionZoneHeading()
    local heading=A.zoneHeading;if not heading or not A.map then return end
    heading:ClearAllPoints()
    if modern() then
        local viewport=A.map.ScrollContainer
        heading:SetPoint('TOP',viewport,'TOP',0,-10);heading:SetJustifyH('CENTER')
        heading:SetWidth(math.max(80,viewport:GetWidth()-48))
    else
        heading:SetPoint('LEFT',A.bar,'LEFT',12,0);heading:SetJustifyH('LEFT')
        local brand=A.brandText and A.brandText:GetStringWidth() or 0
        heading:SetWidth(math.max(80,A.bar:GetWidth()-32-brand))
    end
end
function T.MapMaterial(f,role)
    if not f.mapperlyBrown then
        local base=f:CreateTexture(nil,'BACKGROUND',nil,-2);base:SetAllPoints(f)
        base:SetColorTexture(.16,.10,.055,1);f.mapperlyBrownBase=base
        f.mapperlyBrown=f:CreateTexture(nil,'BACKGROUND',nil,-1);f.mapperlyBrown:SetAllPoints(f)
    end
    local texture=f.mapperlyBrown
    if not modern() then texture:Hide();f.mapperlyBrownBase:Hide();return end
    -- NineSlice TopEdge is border art with size-dependent UVs, not a fill.
    -- Tile the native leather background over a stable warm-brown base instead.
    texture:SetTexture('Interface\\DialogFrame\\UI-DialogBox-Background')
    texture:SetTexCoord(0,1,0,1);texture:SetHorizTile(true);texture:SetVertTile(true)
    texture:SetVertexColor(1,1,1,1);texture:SetAlpha(.35)
    f.mapperlyBrownBase:Show();texture:Show()
end
function T.RefreshMapMaterials()
    if A.footer then T.MapMaterial(A.footer,'footer') end
    if A.actionRail then T.MapMaterial(A.actionRail,'rail') end
end
local function chrome(f,title)
    if f.themeChrome then return f.themeChrome end
    local ok,c=pcall(CreateFrame,'Frame',nil,f,'PortraitFrameTemplate')
    local fallback=not ok or not object(c)
    if fallback then
        c=CreateFrame('Frame',nil,f,'BackdropTemplate')
        c:SetBackdrop({bgFile='Interface\\DialogFrame\\UI-DialogBox-Background',edgeFile='Interface\\DialogFrame\\UI-DialogBox-Border',edgeSize=24,tile=true,tileSize=32,insets={left=6,right=6,top=6,bottom=6}})
        c:SetBackdropColor(.19,.18,.16,1)
    end
    f.themeChrome=c;c.mapperlyFallback=fallback;c:SetAllPoints(f);c:SetFrameLevel(f:GetFrameLevel());c:EnableMouse(false)
    local titleProvided=false
    if type(c.SetTitle)=='function' then titleProvided=pcall(c.SetTitle,c,title) end
    if not titleProvided then
        local titleText=object(c.TitleText) and c.TitleText or object(c.TitleContainer) and c.TitleContainer.TitleText
        if object(titleText) and type(titleText.SetText)=='function' then titleProvided=pcall(titleText.SetText,titleText,title) end
    end
    c.mapperlyFallback=fallback or not titleProvided
    if object(c.CloseButton) then c.CloseButton:Hide() end
    if object(c.Bg) then c.Bg:SetVertexColor(.85,.85,.85,1) end
    local container=object(c.PortraitContainer) and c.PortraitContainer or c
    local portrait=object(c.portrait) and c.portrait or object(container.portrait) and container.portrait
    if not portrait then portrait=c:CreateTexture(nil,'ARTWORK') end
    portrait:ClearAllPoints();portrait:SetPoint('CENTER',container,'TOPLEFT',26,-24);portrait:SetSize(58,58)
    portrait:SetTexture('Interface\\AddOns\\Mapperly\\Media\\Portrait')
    portrait:SetTexCoord(0,1,0,1);portrait:SetVertexColor(1,1,1,1)
    if object(c.PortraitContainer) and object(c.PortraitContainer.CircleMask) then
        local mask=c.PortraitContainer.CircleMask
        mask:ClearAllPoints();mask:SetAllPoints(portrait)
    elseif c.CreateMaskTexture and portrait.AddMaskTexture then
        local mask=c:CreateMaskTexture(nil,'ARTWORK')
        mask:SetTexture('Interface\\CharacterFrame\\TempPortraitAlphaMask');mask:SetAllPoints(portrait)
        portrait:AddMaskTexture(mask);c.themePortraitMask=mask
    end
    c.themePortrait=portrait
    return c
end
local function apply(f,entry)
    local new=modern();f.mapperlyThemeStyle=new and 'gatherly' or 'original'
    local role=entry.role
    if role=='window' then
        if new then
            f:SetBackdrop(nil);local c=chrome(f,entry.title);c:Show()
            if not f.themeWindowBase then
                local base=f:CreateTexture(nil,'BACKGROUND',nil,-8);f.themeWindowBase=base
                base:SetPoint('TOPLEFT',f,'TOPLEFT',6,-24);base:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-6,6);base:SetColorTexture(.09,.07,.045,1)
            end
            f.themeWindowBase:Show()
            if object(c.Bg) then c.Bg:SetVertexColor(.9,.78,.62,1);c.Bg:SetAlpha(1) end
            if entry.titleLabel then entry.titleLabel:SetShown(c.mapperlyFallback) end
            if entry.logo then entry.logo:Hide() end
        else
            if f.themeChrome then f.themeChrome:Hide() end
            if f.themeWindowBase then f.themeWindowBase:Hide() end
            f:SetBackdrop(originalWindow);f:SetBackdropColor(.035,.04,.05,1)
            if entry.titleLabel then entry.titleLabel:Show() end
            if entry.logo then entry.logo:Show() end
        end
    elseif role=='compactWindow' then
        if new then
            f:SetBackdrop(nil)
            if not f.themeChrome then
                -- Same native frame family as the map, without its portrait slot.
                -- Forever SharedUIPanelTemplates: DefaultPanelTemplate uses
                -- the ButtonFrameTemplateNoPortrait nine-slice layout.
                local ok,c=pcall(CreateFrame,'Frame',nil,f,'DefaultPanelTemplate')
                if not ok or not object(c) then
                    c=CreateFrame('Frame',nil,f,'BackdropTemplate')
                    c:SetBackdrop({edgeFile='Interface\\DialogFrame\\UI-DialogBox-Border',edgeSize=24,insets={left=6,right=6,top=6,bottom=6}})
                end
                f.themeChrome=c;c.mapperlyNoPortrait=true;c:SetAllPoints(f);c:SetFrameLevel(f:GetFrameLevel());c:EnableMouse(false)
                if object(c.NineSlice) then c.NineSlice:SetFrameLevel(f:GetFrameLevel()) end
                for _,key in ipairs({'Bg','TopTileStreaks','TitleContainer','CloseButton','FrameGlow'}) do if object(c[key]) then c[key]:Hide() end end
                local base=f:CreateTexture(nil,'BACKGROUND',nil,-2);f.compactFill=base
                base:SetPoint('TOPLEFT',f,'TOPLEFT',3,-3);base:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-3,3);base:SetColorTexture(.16,.10,.055,1)
                local leather=f:CreateTexture(nil,'BACKGROUND',nil,-1);f.compactLeather=leather;leather:SetAllPoints(base)
                leather:SetTexture('Interface\\DialogFrame\\UI-DialogBox-Background');leather:SetHorizTile(true);leather:SetVertTile(true);leather:SetAlpha(.35)
            end
            f.themeChrome:Show();f.compactFill:Show();f.compactLeather:Show()
        else
            if f.themeChrome then f.themeChrome:Hide();f.compactFill:Hide();f.compactLeather:Hide() end
            f:SetBackdrop({bgFile='Interface\\Buttons\\WHITE8X8',edgeFile='Interface\\Buttons\\WHITE8X8',edgeSize=1})
            f:SetBackdropColor(.075,.08,.09,1);f:SetBackdropBorderColor(.23,.21,.16,1)
        end
    elseif role=='card' or role=='header' then
        local textured=new and role=='card'
        f:SetBackdrop({bgFile=textured and 'Interface\\FrameGeneral\\UI-Background-Rock' or 'Interface\\Buttons\\WHITE8X8',tile=textured,tileSize=256,edgeFile=new and 'Interface\\Tooltips\\UI-Tooltip-Border' or 'Interface\\Buttons\\WHITE8X8',edgeSize=new and 12 or 1,insets=new and {left=3,right=3,top=3,bottom=3} or nil})
        if textured and not f.themeCardBase then
            local base=f:CreateTexture(nil,'BACKGROUND',nil,-8);f.themeCardBase=base
            base:SetPoint('TOPLEFT',f,'TOPLEFT',3,-3);base:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-3,3);base:SetColorTexture(.08,.065,.045,1)
        end
        if f.themeCardBase then f.themeCardBase:SetShown(textured) end
        if new and role=='header' then f:SetBackdropColor(0,0,0,0);f:SetBackdropBorderColor(0,0,0,0)
        elseif new then f:SetBackdropColor(.8,.72,.58,1);f:SetBackdropBorderColor(.52,.48,.40,1)
        else f:SetBackdropColor(.075,.08,.09,1);f:SetBackdropBorderColor(.23,.21,.16,1) end
    elseif role=='zone' then
        if new then
            f:SetFont(STANDARD_TEXT_FONT or 'Fonts\\FRIZQT__.TTF',18,'OUTLINE')
            f:SetTextColor(1,1,1,1);f:SetShadowColor(0,0,0,1);f:SetShadowOffset(1,-1)
        else
            if entry.originalFont then f:SetFont(unpack(entry.originalFont)) else f:SetFontObject('GameFontNormal') end
            f:SetTextColor(unpack(entry.originalTextColor or {1,.82,0,1}))
            f:SetShadowColor(unpack(entry.originalShadowColor or {0,0,0,1}));f:SetShadowOffset(unpack(entry.originalShadowOffset or {1,-1}))
        end
        T.PositionZoneHeading()
    elseif role=='text' then
        local color
        if entry.kind=='coordinate' then color=new and {.94,.88,.75} or {1,.82,0}
        elseif entry.kind=='gold' then color=new and {1,.82,.35} or {1,.82,0}
        elseif entry.kind=='muted' then color=new and {.72,.67,.57} or {.5,.5,.5}
        elseif entry.kind=='error' then color={1,.1,.1}
        else color=new and {.94,.88,.75} or {1,1,1} end
        f:SetTextColor(unpack(not new and entry.originalTextColor or color))
        f:SetShadowColor(unpack(not new and entry.originalShadowColor or {0,0,0,1}))
        f:SetShadowOffset(unpack(not new and entry.originalShadowOffset or {1,-1}))
    elseif role=='field' then
        if not f.themeFill then
            f.themeFill=f:CreateTexture(nil,'BACKGROUND',nil,-8);f.themeFill:SetAllPoints(f)
        end
        f.themeFill:SetColorTexture(.15,.145,.13,new and 1 or 0)
        f:SetTextColor(new and .94 or 1,new and .88 or 1,new and .75 or 1)
    elseif role=='button' then f:UpdateVisual()
    elseif role=='trim' then
        f:SetShown(new)
        if A.brandText then A.brandText:SetShown(not new) end
    elseif role=='mapbar' or role=='footer' or role=='rail' then
        if new then f:SetBackdrop(nil)
        else
            f:SetBackdrop({bgFile='Interface\\Tooltips\\UI-Tooltip-Background'})
            if role=='rail' then f:SetBackdropColor(.025,.027,.03,1) else f:SetBackdropColor(.025,.022,.018,1) end
        end
        if role~='mapbar' then T.MapMaterial(f,role) end
    end
end
local function capture(f,method,count)
    if type(f[method])~='function' then return end
    local values={pcall(f[method],f)}
    if not values[1] then return end
    for i=2,count+1 do if type(values[i])~='number' then return end end
    table.remove(values,1);return values
end
function T.Register(f,role,extra)
    local entry=extra or {};entry.role=role
    if role=='text' or role=='zone' then
        local previous=registry[f]
        entry.originalTextColor=previous and previous.originalTextColor or capture(f,'GetTextColor',4)
        entry.originalShadowColor=previous and previous.originalShadowColor or capture(f,'GetShadowColor',4)
        entry.originalShadowOffset=previous and previous.originalShadowOffset or capture(f,'GetShadowOffset',2)
        if role=='zone' and type(f.GetFont)=='function' then
            local ok,path,size,flags=pcall(f.GetFont,f)
            if ok and type(path)=='string' and type(size)=='number' then entry.originalFont={path,size,flags or ''} end
        end
    end
    registry[f]=entry;apply(f,entry);return f
end
function T.Label(t,font)
    local kind=font and (font:find('Disable',1,true) and 'muted' or font:find('Red',1,true) and 'error' or font:find('Normal',1,true) and 'gold') or 'body'
    return T.Register(t,'text',{kind=kind})
end
function T.ButtonRole(b,role) b.themeButtonRole=role;b:UpdateVisual();return b end
function T.MapChrome(parent)
    local trim=CreateFrame('Frame',nil,parent);trim:SetAllPoints(parent);trim:EnableMouse(false)
    trim:SetFrameStrata('HIGH');trim:SetFrameLevel(parent:GetFrameLevel()+140)
    local c=chrome(trim,A.version and 'Mapperly '..A.version or 'Mapperly')
    if object(c.Bg) then c.Bg:Hide() end
    -- PortraitFrame's NineSlice normally uses an elevated frame level. Keep
    -- map trim below our right-hand controls rather than covering their edges.
    if object(c.NineSlice) then c.NineSlice:SetFrameLevel(trim:GetFrameLevel()+1) end
    T.Register(trim,'trim');return trim
end
local function nativeArt(b,role)
    local key=role=='tab' and 'themeNativeTab' or 'themeNativeButton'
    if b[key..'Unavailable'] then return end
    if b[key] then return b[key] end
    local ok,frame=pcall(CreateFrame,'Button',nil,b,role=='tab' and 'PanelTopTabButtonTemplate' or 'UIPanelButtonTemplate')
    if not ok or not object(frame) then b[key..'Unavailable']=true;return end
    if role=='tab' and (not object(frame.Left) or not object(frame.Middle) or not object(frame.Right)) then
        frame:Hide();b[key..'Unavailable']=true;return
    end
    frame:SetAllPoints(b);frame:SetFrameLevel(b:GetFrameLevel()+1);frame:EnableMouse(false)
    frame:SetText('')
    local nativeText=frame:GetFontString()
    if object(nativeText) then
        nativeText:ClearAllPoints();nativeText:SetPoint('CENTER',frame,'CENTER',0,0)
        nativeText:SetSize(math.max(1,b:GetWidth()-18),24);nativeText:SetJustifyH('CENTER')
    end
    -- The caption belongs to the native skin itself. A FontString assigned to
    -- the outer button can render below this child frame in the live client.
    local caption=frame:CreateFontString(nil,'OVERLAY','GameFontNormal');frame.mapperlyCaption=caption
    caption:SetPoint('CENTER',frame,'CENTER',0,0);caption:SetJustifyH('CENTER');caption:SetWordWrap(false)
    b[key]=frame;return frame
end
function T.PaintButton(b)
    local new=modern();local role=b.themeButtonRole
    local art=new and not b.iconOnly and (role=='primary' or role=='choice' or role=='tab') and nativeArt(b,role) or nil
    if art and role=='tab' then
        -- Classic and Mainline tab helpers use different active-region names.
        -- Let the installed helper validate its template, and retain quiet art
        -- if the template and helper do not belong to the same client family.
        local helper=b.active and PanelTemplates_SelectTab or PanelTemplates_DeselectTab
        if type(helper)~='function' or not pcall(helper,art) then
            art:Hide();b.themeNativeTabUnavailable=true;art=nil
        end
    end
    for _,key in ipairs({'themeNativeButton','themeNativeTab'}) do if b[key] then b[key]:SetShown(b[key]==art) end end
    local visible=not b.iconOnly and not art
    b.outer:SetShown(visible);b.rim:SetShown(visible)
    for _,edge in ipairs(b.borders) do edge:SetShown(visible) end
    b.face:SetShown(not art)
    b.caption:SetShown(not b.iconOnly and not art)
    if art then
        local nativeText=art:GetFontString()
        art.mapperlyCaption:ClearAllPoints()
        art.mapperlyCaption:SetPoint('CENTER',object(nativeText) and nativeText or art,'CENTER',0,0)
        art.mapperlyCaption:SetText(b:GetText());art.mapperlyCaption:SetSize(math.max(1,b:GetWidth()-18),24)
        if b:IsEnabled() then art.mapperlyCaption:SetTextColor(1,.82,.35) else art.mapperlyCaption:SetTextColor(.5,.5,.5) end
        art.mapperlyCaption:Show()
        b.activeLine:Hide()
        if role~='tab' then
            art:SetEnabled(b:IsEnabled());art:SetButtonState((b.pressed or role=='choice' and b.active) and 'PUSHED' or 'NORMAL')
            if b.hover then art:LockHighlight() else art:UnlockHighlight() end
        end
        if role=='choice' and not art.mapperlySelectedMark then
            local mark=art:CreateTexture(nil,'OVERLAY');art.mapperlySelectedMark=mark
            mark:SetTexture('Interface\\Buttons\\UI-CheckBox-Check');mark:SetSize(18,18);mark:SetPoint('LEFT',art,'LEFT',6,0)
        end
        if art.mapperlySelectedMark then art.mapperlySelectedMark:SetShown(role=='choice' and b.active) end
    end
    if new then
        local fill=b.pressed and {.18,.12,.08} or b.hover and {.30,.24,.16} or b.active and {.27,.21,.12} or {.15,.145,.13}
        local rim=b.active and {.71,.56,.29} or {.52,.48,.40}
        b.face:SetColorTexture(fill[1],fill[2],fill[3],1);b.rim:SetColorTexture(rim[1],rim[2],rim[3],1)
        if b.iconOnly and not b.hover and not b.pressed and not b.active then b.face:SetColorTexture(0,0,0,0) end
        for _,edge in ipairs(b.borders) do edge:SetColorTexture(rim[1],rim[2],rim[3],1) end
        b.caption:SetTextColor(1,.82,.35)
    end
    b.mapperlyThemeStyle=new and 'gatherly' or 'original'
end
function T.QuestBackground(scroll,background)
    if not scroll or not background then return end
    if not scroll.mapperlyThemeBackground then
        local t=scroll:CreateTexture(nil,'BACKGROUND',nil,-8);t:SetAllPoints(scroll);t:SetColorTexture(.19,.18,.16,1)
        scroll.mapperlyThemeBackground=t;scroll.mapperlyOriginalBackgroundAlpha=background:GetAlpha()
    end
    local new=modern();scroll.mapperlyThemeBackground:SetShown(new)
    background:SetAlpha(new and 0 or scroll.mapperlyOriginalBackgroundAlpha)
end
function T.Apply()
    T.revision=(T.revision or 0)+1
    for f,entry in pairs(registry) do apply(f,entry) end
    if A.FitQuestBackground then A.FitQuestBackground() end
    if A.map and A.AttachZoneLevels then A.AttachZoneLevels() end
end
function T.Set(name)
    if name~='gatherly' and name~='original' then return false end
    local changed=A.db.theme~=name
    A.db.theme=name;T.Apply()
    if changed and A.map and A.ApplyLayout then A.ApplyLayout() end
    if A.SyncSettings then A.SyncSettings() end
    return true
end
