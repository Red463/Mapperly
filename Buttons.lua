local _,A=...
-- Solid charcoal controls with a thin bronze rim and no bevel or gradient.
function A.CreateMapButton(parent,text,width,x,callback)
    local b=CreateFrame('Button',nil,parent)
    b:SetSize(width+16,28);b:SetPoint('LEFT',parent,'LEFT',x,0)
    local function panel(inset,level)
        local t=b:CreateTexture(nil,'BACKGROUND',nil,level)
        t:SetPoint('TOPLEFT',b,'TOPLEFT',inset,-inset)
        t:SetPoint('BOTTOMRIGHT',b,'BOTTOMRIGHT',-inset,inset)
        return t
    end
    b.outer=panel(0,0);b.outer:SetColorTexture(.09,.085,.065,1)
    b.rim=panel(1,1)
    b.face=panel(2,2)
    local function edge(a,ap,ax,ay,c,cp,cx,cy,vertical)
        local t=b:CreateTexture(nil,'BORDER')
        t:SetPoint(a,b,ap,ax,ay);t:SetPoint(c,b,cp,cx,cy)
        if vertical then t:SetWidth(1) else t:SetHeight(1) end
        return t
    end
    -- Explicit foreground edges avoid losing a thin background rim at fractional
    -- UI scales, particularly when the zone heading is resized independently.
    b.topBorder=edge('TOPLEFT','TOPLEFT',0,0,'TOPRIGHT','TOPRIGHT',0,0)
    b.bottomBorder=edge('BOTTOMLEFT','BOTTOMLEFT',0,0,'BOTTOMRIGHT','BOTTOMRIGHT',0,0)
    b.leftBorder=edge('TOPLEFT','TOPLEFT',0,0,'BOTTOMLEFT','BOTTOMLEFT',0,0,true)
    b.rightBorder=edge('TOPRIGHT','TOPRIGHT',0,0,'BOTTOMRIGHT','BOTTOMRIGHT',0,0,true)
    b.borders={b.topBorder,b.bottomBorder,b.leftBorder,b.rightBorder}
    for _,t in ipairs(b.borders) do
        t:SetSnapToPixelGrid(true);t:SetTexelSnappingBias(0)
    end
    b.activeLine=edge('BOTTOMLEFT','BOTTOMLEFT',9,5,'BOTTOMRIGHT','BOTTOMRIGHT',-9,5)
    b.activeLine:SetHeight(1);b.activeLine:SetColorTexture(.89,.74,.41,1)
    local caption=b:CreateFontString(nil,'OVERLAY','GameFontNormal');b.caption=caption
    caption:SetJustifyH('CENTER');caption:SetWordWrap(false)
    b:SetFontString(caption);b:SetText(text)
    -- Measure the actual Blizzard font instead of assuming fixed character widths.
    b:SetWidth(math.max(width+16,math.ceil(caption:GetStringWidth())+24))
    function b:UpdateVisual()
        local pressed,hover,active=self.pressed,self.hover,self.active
        local fill,rim={.105,.11,.12},{.55,.48,.32}
        if active then fill={.16,.155,.13};rim={.867,.729,.424} end
        if hover then fill={.18,.185,.195};rim={.82,.694,.42} end
        if pressed then fill={.065,.07,.08};rim={.72,.60,.36} end
        self.rim:SetColorTexture(rim[1],rim[2],rim[3],1)
        for _,t in ipairs(self.borders) do t:SetColorTexture(rim[1],rim[2],rim[3],1) end
        self.face:SetColorTexture(fill[1],fill[2],fill[3],1)
        if active then self.activeLine:Show() else self.activeLine:Hide() end
        caption:SetTextColor((active or hover) and 1 or .945,hover and .929 or active and .886 or .835,hover and .737 or active and .608 or .58)
        caption:ClearAllPoints()
        if self.iconOnly then
            caption:Hide()
            self.icon:ClearAllPoints();self.icon:SetPoint('CENTER',self,'CENTER',0,0)
            self.icon:SetVertexColor(pressed and .75 or 1,pressed and .75 or 1,pressed and .75 or 1)
        elseif self.icon then
            caption:SetWidth(18)
            caption:SetPoint('RIGHT',self,'RIGHT',-12,0)
            self.icon:ClearAllPoints();self.icon:SetPoint('LEFT',self,'LEFT',14,0)
        else caption:SetWidth(math.max(1,self:GetWidth()-18));caption:SetPoint('CENTER',self,'CENTER',0,0) end
        if A.Theme then A.Theme.PaintButton(self) end
    end
    b:UpdateVisual()
    b:SetScript('OnEnter',function(self) self.hover=true;self:UpdateVisual() end)
    b:SetScript('OnLeave',function(self) self.hover=false;self.pressed=false;self:UpdateVisual() end)
    b:SetScript('OnMouseDown',function(self) self.pressed=true;self:UpdateVisual() end)
    b:SetScript('OnMouseUp',function(self) self.pressed=false;self:UpdateVisual() end)
    b:SetScript('OnClick',callback)
    if A.Theme then A.Theme.Register(b,'button') end
    return b
end
function A.CreateIconButton(parent,asset,callback)
    local b=A.CreateMapButton(parent,'',12,0,callback)
    b.iconOnly=true;b:SetSize(28,28)
    b.outer:Hide();b.rim:Hide()
    for _,edge in ipairs(b.borders) do edge:Hide() end
    b.face:ClearAllPoints();b.face:SetAllPoints(b)
    b.icon=b:CreateTexture(nil,'ARTWORK');b.icon:SetSize(24,24)
    b.icon:SetTexture(asset=='Navigate' and 'Interface\\AddOns\\Mapperly\\Media\\GuideArrow' or 'Interface\\AddOns\\Mapperly\\Media\\Toolbar\\Small\\'..asset)
    b.icon:SetSnapToPixelGrid(true);b.icon:SetTexelSnappingBias(0)
    b:UpdateVisual()
    return b
end
function A.AttachButtonTooltip(button,text)
    button.tooltipText=text
    function button:RefreshTooltip()
        if not self.hover or not self:IsVisible() or not GameTooltip:IsOwned(self) then return end
        local value=type(self.tooltipText)=='function' and self.tooltipText() or self.tooltipText
        if value~=self.tooltipShownText then
            GameTooltip:SetText(value);self.tooltipShownText=value;GameTooltip:Show()
        end
    end
    button:HookScript('OnEnter',function(self)
        GameTooltip:SetOwner(self,'ANCHOR_LEFT');self.tooltipShownText=nil;self:RefreshTooltip()
    end)
    button:HookScript('OnLeave',function(self)
        if GameTooltip:IsOwned(self) then GameTooltip:Hide() end
        self.tooltipShownText=nil
    end)
    button:HookScript('OnClick',function() button:RefreshTooltip() end)
    button:HookScript('OnHide',function(self)
        if GameTooltip:IsOwned(self) then GameTooltip:Hide() end
        self.hover=false;self.tooltipShownText=nil
    end)
end
function A.UpdateButtonStates()
    if not A.db then return end
    local navigate=A.controls and A.controls.navigate
    if navigate then navigate.active=A.Navigation and A.Navigation.target~=nil or false;navigate:UpdateVisual() end
    if A.sizeButton then
        local asset=A.db.compact and 'Resize' or 'Compact'
        if A.sizeButton.iconAsset~=asset then
            A.sizeButton.icon:SetTexture('Interface\\AddOns\\Mapperly\\Media\\Toolbar\\Small\\'..asset)
            A.sizeButton.iconAsset=asset
        end
    end
    for key,setting in pairs({quests='questPane',reveal='reveal',lock='locked'}) do
        local b=A.controls and A.controls[key]
        if b then
            b.active=not not A.db[setting]
            if key=='quests' and b.arrow then b.arrow:SetText(b.active and '<' or '>') end
            b:UpdateVisual()
        end
    end
    for _,button in pairs(A.controls or {}) do
        if button.RefreshTooltip then button:RefreshTooltip() end
    end
end
