-- Minimal native frame double. Real geometry and domain logic remain production code.
function fakeUI()
 local methods={}
 function methods:SetScript(k,v) self.scripts[k]=v end
 function methods:GetScript(k) return self.scripts[k] end
 function methods:HookScript(k,v) local old=self.scripts[k]; self.scripts[k]=function(...) if old then old(...) end; v(...) end end
 function methods:SetPoint(...) self.point={...} end
 function methods:SetAllPoints(target) self.all=target or self.parent end
 function methods:SetText(t) self.text=t; if rawget(self,'fontString') then self.fontString:SetText(t) end end
 function methods:SetTitle(text) self.title=text end
 function methods:SetFontString(t) self.fontString=t end
 function methods:GetFontString() return self.fontString end
 function methods:SetColorTexture(r,g,b,a) self.color={r,g,b,a or 1} end
 function methods:SetGradientAlpha(orientation,r1,g1,b1,a1,r2,g2,b2,a2)
  self.gradient={orientation=orientation,left={r1,g1,b1,a1},right={r2,g2,b2,a2}}
  self.color={(r1+r2)/2,(g1+g2)/2,(b1+b2)/2,(a1+a2)/2}
 end
 function methods:SetGradient(orientation,left,right) methods.SetGradientAlpha(self,orientation,left.r,left.g,left.b,left.a,right.r,right.g,right.b,right.a) end
 function methods:SetTextColor(r,g,b,a) self.textColor={r,g,b,a or 1} end
 function methods:SetFont(path,size,flags) self.fontPath=path;self.fontSize=size;self.fontFlags=flags end
 function methods:SetScale(v) self.scale=v end
 function methods:GetZoom() return self.zoom or 0 end
 function methods:SetZoom(v) self.zoom=v end
 function methods:SetOrientation(v) self.orientation=v end
 function methods:SetAlpha(v) self.alpha=v end
 function methods:GetAlpha() return self.alpha or 1 end
 function methods:IsEnabled() return self.enabled~=false end
 function methods:GetText() return self.text or '' end
 function methods:SetSize(w,h) self.width=w; self.height=h end
 function methods:SetWidth(w) self.width=w end
 function methods:SetChecked(v) self.checked=not not v end
 function methods:GetChecked() return self.checked end
 function methods:SetValue(v) local changed=self.value~=v;self.value=v;if changed and self.scripts.OnValueChanged then self.scripts.OnValueChanged(self,v) end end
 function methods:SetMinMaxValues(lo,hi) self.minimum=lo;self.maximum=hi end
 function methods:GetMinMaxValues() return self.minimum,self.maximum end
 function methods:SetScrollChild(child) self.scrollChild=child;child.scrollOwner=self end
 function methods:GetScrollChild() return self.scrollChild end
 function methods:SetVerticalScroll(value) self.verticalScroll=value end
 function methods:GetVerticalScroll() return self.verticalScroll or 0 end
 function methods:SetHeight(h) self.height=h end
 function methods:SetParent(p) self.parent=p end
 function methods:GetParent() return self.parent end
 function methods:GetWidth() local all=rawget(self,'all');return all and all:GetWidth() or rawget(self,'width') or 500 end
 function methods:GetHeight() local all=rawget(self,'all');return all and all:GetHeight() or rawget(self,'height') or 500 end
 function methods:Show() local changed=self.shown==false;self.shown=true;if changed and self.scripts.OnShow then self.scripts.OnShow(self) end end
 function methods:Hide() local changed=self.shown~=false;self.shown=false;if changed and self.scripts.OnHide then self.scripts.OnHide(self) end end
 function methods:IsShown() return self.shown~=false end
 function methods:SetShown(shown) if shown then self:Show() else self:Hide() end end
 function methods:IsVisible() return self:IsShown() and (not self.parent or self.parent:IsVisible()) end
 function methods:Enable() self:SetEnabled(true) end
 function methods:Disable() self:SetEnabled(false) end
 function methods:SetEnabled(v) local changed=self.enabled~=v; self.enabled=v; local f=self.scripts[v and 'OnEnable' or 'OnDisable']; if changed and f then f(self) end end
 function methods:SetTexCoord(...) self.coords={...} end
 function methods:SetNormalTexture(v) self.normalTexture=v end
 function methods:SetTexture(v) self.texture=v end
 function methods:SetVertexColor(...) self.vertexColor={...};self.gradient=nil end
 function methods:EnableMouse(v) self.mouse=v;self.mouseClicks=v;self.mouseMotion=v end
 function methods:EnableMouseMotion(v) self.mouseMotion=v end
 function methods:SetBackdrop(v) self.backdrop=v end
 function methods:SetStartPoint(anchor,parent,x,y) self.lineStart={anchor,parent,x,y} end
 function methods:SetEndPoint(anchor,parent,x,y) self.lineEnd={anchor,parent,x,y} end
 function methods:SetThickness(v) self.thickness=v end
 function methods:SetDrawLayer(layer,sublevel) self.drawLayer=layer;self.drawSublevel=sublevel or 0 end
 function methods:GetDrawLayer() return self.drawLayer or 'OVERLAY',self.drawSublevel or 0 end
 function methods:SetRotation(v) self.rotation=v end
 function methods:GetPoint() return 'CENTER',nil,'CENTER',0,0 end
 function methods:GetEffectiveScale() return 1 end
 function methods:GetFrameLevel() return self.frameLevel or 1 end
 function methods:SetFrameLevel(value) self.frameLevel=value end
 function methods:GetFrameStrata() return self.frameStrata or self.parent and self.parent:GetFrameStrata() or 'MEDIUM' end
 function methods:SetFrameStrata(value) self.frameStrata=value end
 function methods:CreateFontString() return CreateFrame('FontString',nil,self) end
 function methods:CreateTexture() return CreateFrame('Texture',nil,self) end
 function methods:CreateMaskTexture() return CreateFrame('MaskTexture',nil,self) end
 function methods:AddMaskTexture(mask) self.masks=self.masks or {};self.masks[#self.masks+1]=mask end
 function methods:CreateLine() return CreateFrame('Line',nil,self) end
 CreateFrame=function(kind,name,parent,template)
  if template=='CharacterFrameTabButtonTemplate' then error("CreateFrame(): Couldn't find inherited node CharacterFrameTabButtonTemplate") end
  local o={kind=kind,name=name,parent=parent,template=template,scripts={},shown=true,enabled=true,frameLevel=parent and parent:GetFrameLevel()+1 or 1}
  local frame=setmetatable(o,{__index=function(_,k) if methods[k] then return methods[k] end; if k:match('^%u') then return function() end end end})
  if template=='PanelTabButtonTemplate' or template=='PanelTopTabButtonTemplate' then
   for _,key in ipairs({'Left','Middle','Right','LeftActive','MiddleActive','RightActive'}) do frame[key]=CreateFrame('Texture',nil,frame) end
   frame.Text=CreateFrame('FontString',nil,frame);frame.fontString=frame.Text
  end
  return frame
 end
 PanelTemplates_TabResize=function(tab,_,width) assert(type(tab.Text)=='table' and type(tab.Left)=='table');tab:SetWidth(width or 100) end
 PanelTemplates_SelectTab=function(tab) assert(type(tab.LeftActive)=='table');tab:Disable() end
 PanelTemplates_DeselectTab=function(tab) assert(type(tab.Left)=='table');tab:Enable() end
 UIParent=CreateFrame('Frame');UIParent:SetSize(1920,1080); Minimap=CreateFrame('Frame'); Minimap:SetSize(200,200)
 WorldMapFrame=CreateFrame('Frame'); WorldMapFrame.ScrollContainer=CreateFrame('Frame'); WorldMapFrame.canvas=CreateFrame('Frame',nil,WorldMapFrame)
 WorldMapFrame.GetCanvas=function(self) return self.canvas end
 WorldMapFrame.GetMapID=function() return 1 end
 WorldMapFrame.ScrollContainer.GetNormalizedCursorPosition=function() return .25,.4 end
 GameTooltip=CreateFrame('Frame'); SlashCmdList={}; UISpecialFrames={}
end
