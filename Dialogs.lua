local _,A=...
local U={};A.Dialogs=U
function U.Label(parent,text,x,y,font)
    local t=parent:CreateFontString(nil,'OVERLAY',font or 'GameFontHighlight')
    t:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y);t:SetText(text)
    if A.Theme then A.Theme.Label(t,font) end
    return t
end
function U.Card(parent,x,y,w,h)
    local c=CreateFrame('Frame',nil,parent,'BackdropTemplate');c:SetSize(w,h);c:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y)
    c:SetBackdrop({bgFile='Interface\\Buttons\\WHITE8X8',edgeFile='Interface\\Buttons\\WHITE8X8',edgeSize=1})
    c:SetBackdropColor(.075,.08,.09,1);c:SetBackdropBorderColor(.23,.21,.16,1)
    if A.Theme then A.Theme.Register(c,'card') end
    return c
end
function U.CompactWindow(parent,w,h)
    local f=U.Card(parent,0,0,w,h)
    if A.Theme then A.Theme.Register(f,'compactWindow') end
    return f
end
function U.Action(parent,text,x,y,w,fn,role)
    local b=A.CreateMapButton(parent,text,w-16,0,fn)
    b:ClearAllPoints();b:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y);b:SetSize(w,28)
    local setText=b.SetText
    function b:SetText(value)
        setText(self,value)
        for _,key in ipairs({'themeNativeButton','themeNativeTab'}) do
            local art=self[key];if art and art.mapperlyCaption then art.mapperlyCaption:SetText(self:GetText()) end
        end
    end
    local setEnabled=b.SetEnabled
    function b:SetEnabled(value) setEnabled(self,value);self:UpdateVisual() end
    if A.Theme and text~='' then A.Theme.ButtonRole(b,role or 'primary') else b:UpdateVisual() end
    return b
end
function U.Input(parent,x,y,w,h,max,multiline)
    local e=CreateFrame('EditBox',nil,parent,'InputBoxTemplate');e:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y);e:SetSize(w,h or 28)
    e:SetAutoFocus(false);e:SetMaxLetters(max or 120)
    if multiline then e:SetMultiLine(true);e:SetFontObject('GameFontHighlight');e:SetTextInsets(4,4,4,4) end
    if A.Theme then A.Theme.Register(e,'field') end
    return e
end
local function window(name,title,subtitle,w,h,compactHeader)
    local f=CreateFrame('Frame',name,UIParent,'BackdropTemplate');f:SetSize(w,h);f:SetPoint('CENTER');f:SetFrameStrata('DIALOG')
    f:SetClampedToScreen(true);f:SetMovable(true);f:EnableMouse(true);f:RegisterForDrag('LeftButton')
    f:SetScript('OnDragStart',function(s) s:StartMoving() end);f:SetScript('OnDragStop',function(s) s:StopMovingOrSizing() end)
    f:SetBackdrop({bgFile='Interface\\Buttons\\WHITE8X8',edgeFile='Interface\\DialogFrame\\UI-DialogBox-Border',edgeSize=24,insets={left=6,right=6,top=6,bottom=6}})
    f:SetBackdropColor(.035,.04,.05,1)
    local inset=compactHeader and 6 or 12
    local heading=U.Card(f,inset,inset,w-2*inset,compactHeader and 38 or 64)
    local icon=heading:CreateTexture(nil,'ARTWORK');local iconSize=compactHeader and 28 or 46
    icon:SetSize(iconSize,iconSize);icon:SetPoint('LEFT',heading,'LEFT',8,0);icon:SetTexture('Interface\\AddOns\\Mapperly\\Media\\Portrait')
    local x=compactHeader and 51 or 68
    local titleLabel=U.Label(heading,title,x,compactHeader and 2 or 13,'GameFontNormalLarge')
    local detail=U.Label(heading,subtitle,x,compactHeader and 22 or 38,'GameFontDisableSmall')
    if compactHeader then
        for _,label in ipairs({titleLabel,detail}) do
            label:SetWidth(w-2*inset-x-28);label:SetWordWrap(false);label:SetJustifyH('LEFT')
        end
        f.toolWidth=w;f.toolHeight=h
    end
    f.themeTitleLabel=titleLabel
    local close=CreateFrame('Button',nil,heading,'UIPanelCloseButton');close:SetPoint('TOPRIGHT',heading,'TOPRIGHT',0,0);close:SetScript('OnClick',function() f:Hide() end)
    if A.Theme then
        A.Theme.Register(heading,'header');A.Theme.Register(f,'window',{title=title,titleLabel=titleLabel,logo=icon})
    end
    UISpecialFrames=UISpecialFrames or {};table.insert(UISpecialFrames,name);return f
end
function U.Window(name,title,subtitle,w,h)
    return window(name,title,subtitle,w,h,false)
end
function U.ToolWindow(name,title,subtitle,w,h)
    return window(name,title,subtitle,w,h,true)
end
function U.Show(f,drawerKey)
    if drawerKey and A.map and A.map:IsShown() then
        A.SelectMapDrawer(drawerKey,f)
        return
    end
    if A.drawerWindow==f then A.SelectMapDrawer(nil) end
    f:SetScale(math.min(1,(UIParent:GetWidth()-40)/f:GetWidth(),(UIParent:GetHeight()-40)/f:GetHeight()))
    if CloseDropDownMenus then CloseDropDownMenus() end
    f:Show();f:Raise()
end
function U.Tabs(tabs,selected)
    for key,tab in pairs(tabs) do tab.active=key==selected;if A.Theme then A.Theme.ButtonRole(tab,'tab') else tab:UpdateVisual() end end
end
function U.List(parent,x,y,w,h,options)
    local scroll=CreateFrame('ScrollFrame',nil,parent,'UIPanelScrollFrameTemplate');scroll:SetPoint('TOPLEFT',parent,'TOPLEFT',x,-y);scroll:SetSize(w-28,h)
    local child=CreateFrame('Frame',nil,scroll);child:SetSize(w-28,1);scroll:SetScrollChild(child)
    local list={frame=scroll,child=child,rows={},width=w-28}
    local rowHeight=options and options.rowHeight or 58
    local stride=rowHeight+(options and options.rowGap or 6)
    local textX=options and 36 or 40
    function list:Render(records,render)
        for _,row in ipairs(self.rows) do row:Hide();row.record=nil end
        for i,p in ipairs(records) do
            local row=self.rows[i]
            if not row then
                row=U.Card(child,0,(i-1)*stride,self.width,rowHeight);self.rows[i]=row
                row.icon=row:CreateTexture(nil,'ARTWORK');row.icon:SetSize(24,24);row.icon:SetPoint('TOPLEFT',row,'TOPLEFT',8,-9)
                row.title=U.Label(row,'',textX,options and 4 or 9,'GameFontNormal');row.title:SetWidth(options and self.width-textX-6 or self.width-294);row.title:SetWordWrap(false)
                row.detail=U.Label(row,'',textX,options and 20 or 32,'GameFontDisableSmall');row.detail:SetWidth(self.width-textX-14);row.detail:SetWordWrap(false)
                row.title:SetJustifyH('LEFT');row.detail:SetJustifyH('LEFT')
            end
            row.record=p;render(row,p);row:Show()
        end
        child:SetHeight(math.max(1,#records*stride-(stride-rowHeight)));scroll:SetVerticalScroll(0)
    end
    return list
end
