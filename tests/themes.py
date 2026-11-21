"""Theme persistence, live switching and native styling contracts."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text(encoding='utf-8'))
lua.execute('''
fakeUI();A={};local create=CreateFrame
CreateFrame=function(kind,...)
 local f=create(kind,...)
 local args={...}
 if args[3]=='PortraitFrameTemplate' then
  f.PortraitContainer=create('Frame',nil,f)
  f.PortraitContainer.CircleMask=create('MaskTexture',nil,f.PortraitContainer)
  f.portrait=create('Texture',nil,f.PortraitContainer);f.portrait:SetTexCoord(.25,.75,.25,.75)
 end
 if kind=='FontString' then f.GetStringWidth=function(self) return #self:GetText()*7 end end
 if kind=='Texture' then
  f.GetAtlas=function(self) return self.atlas end;f.SetAtlas=function(self,name) self.atlas=name end
  f.GetTexture=function(self) return self.texture end
  f.GetTexCoord=function(self) return unpack(self.coords or {0,0,0,1,1,0,1,1}) end
 end
 return f
end
C_Map={GetMapInfo=function(id) return {name='Zone '..id} end}
A.Print=function() end;A.Refresh=function() end;A.UpdateOpacity=function() end
''')
for name in ['Store.lua','Theme.lua','Buttons.lua','Pins.lua','Dialogs.lua','NavigationUI.lua','NotesUI.lua','Settings.lua']:
    path=root/name
    if path.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',path.read_text(encoding='utf-8-sig'))
lua.execute('''
assert(A.InitStore({}).theme=='gatherly','approved new theme must be the default')
assert(A.InitStore({theme='invalid'}).theme=='gatherly')
assert(A.InitStore({theme='original'}).theme=='original','saved Original preference must survive reload')
A.InitStore({})
assert(A.Theme,'theme layer must exist')
A.ShowSettings();local settings=A.settingsWindow
assert(A.themeChoices.gatherly.active and not A.themeChoices.original.active)
assert(A.themeChoices.gatherly:GetText()=='Default','theme should be named Default in Settings')
A.ShowNote(1431,.2,.3);local note=A.noteWindow
note.nameInput:SetText('Unsaved title');note.descriptionInput:SetText('Keep my draft')
local icon=note.selectedIcon
A.themeChoices.original:GetScript('OnClick')()
assert(A.db.theme=='original' and A.themeChoices.original.active)
assert(A.noteWindow==note and note.nameInput:GetText()=='Unsaved title' and note.descriptionInput:GetText()=='Keep my draft')
assert(note.selectedIcon==icon and note:IsShown(),'theme switch must preserve editor state and visibility')
assert(note.mapperlyThemeStyle=='original' and settings.mapperlyThemeStyle=='original')
assert(not note.themeChrome:IsShown(),'original theme must hide new portrait chrome')
A.themeChoices.gatherly:GetScript('OnClick')()
assert(note.themeChrome:IsShown() and settings.themeChrome:IsShown())
assert(note.themeChrome.themePortrait.coords[1]==0 and note.themeChrome.themePortrait.coords[2]==1,'portrait texture must clear inherited crop coordinates')
assert(note.themeChrome.PortraitContainer.CircleMask.all==note.themeChrome.themePortrait,'portrait mask must follow actual artwork bounds')
assert(note.editor.mapperlyThemeStyle=='gatherly')
assert(note.save.mapperlyThemeStyle=='gatherly' and note.save.themeNativeButton:IsShown(),'Save uses native red action styling')
for _,b in ipairs({note.save,A.settingsTabs.display,A.settingsTabs.layers}) do
 local art=b.themeNativeButton or b.themeNativeTab
 assert(art.mapperlyCaption and art.mapperlyCaption:GetParent()==art and art.mapperlyCaption:GetText()==b:GetText(),'native skin must own its visible caption above its artwork')
 assert(art.mapperlyCaption:IsShown() and not b.caption:IsShown(),'native buttons must not rely on a caption below their frame')
 if b.themeButtonRole=='tab' then assert(art.mapperlyCaption.point[2]==art:GetFontString(),'tab caption must follow native selected/unselected text positioning') end
end
assert(not note.iconButtons.note_enemy.themeNativeButton,'icon choices must stay quiet')
local late=A.Dialogs.Window('ThemeLateWindow','Late window','Created after switching',360,220)
assert(late.mapperlyThemeStyle=='gatherly' and late.themeChrome:IsShown())
local scroll=CreateFrame('ScrollFrame');local background=scroll:CreateTexture();background:SetAlpha(.8)
A.Theme.QuestBackground(scroll,background)
assert(background:GetAlpha()==0 and scroll.mapperlyThemeBackground:IsShown())
A.Theme.Set('original');A.Theme.QuestBackground(scroll,background)
assert(background:GetAlpha()==.8 and not scroll.mapperlyThemeBackground:IsShown(),'native quest artwork must restore its original alpha')
A.Theme.Set('gatherly')
local create=CreateFrame
CreateFrame=function(kind,name,parent,template)
 if template=='PortraitFrameTemplate' then error('template unavailable') end
 return create(kind,name,parent,template)
end
local fallback=A.Dialogs.Window('ThemeFallback','Fallback title','Subtitle',360,220)
CreateFrame=create
assert(fallback.themeChrome.mapperlyFallback and fallback.themeTitleLabel:IsShown(),'fallback chrome must retain a visible title')
A.Theme.Set('gatherly')
CreateFrame=function(kind,name,parent,template)
 local f=create(kind,name,parent,template)
 if template=='PortraitFrameTemplate' then f.SetTitle=false end
 if template=='PanelTopTabButtonTemplate' then return create('Button',name,parent) end
 return f
end
local incomplete=A.Dialogs.Window('ThemeIncomplete','Keep this title','Subtitle',360,220)
assert(incomplete.themeTitleLabel:IsShown(),'a portrait object without a title API must retain its custom heading')
local tab=A.CreateMapButton(incomplete,'Safe tab',100,0,function() end)
A.Theme.ButtonRole(tab,'tab')
assert(tab.face:IsShown() and (not tab.themeNativeTab or not tab.themeNativeTab:IsShown()),'incomplete native tabs must fall back without throwing')
CreateFrame=create
local text=CreateFrame('FontString');text:SetTextColor(.2,.4,.6,.8)
text.GetTextColor=function(self) return unpack(self.textColor) end
text.SetShadowColor=function(self,...) self.shadowColor={...} end
text.GetShadowColor=function(self) return unpack(self.shadowColor) end
text.SetShadowOffset=function(self,...) self.shadowOffset={...} end
text.GetShadowOffset=function(self) return unpack(self.shadowOffset) end
text:SetShadowColor(.1,.2,.3,.4);text:SetShadowOffset(2,-3)
A.Theme.Label(text,'GameFontHighlight');A.Theme.Set('original')
assert(text.textColor[1]==.2 and text.textColor[4]==.8 and text.shadowColor[1]==.1 and text.shadowOffset[1]==2,'Original must restore inherited text colours and shadows')
for i=1,6 do A.Theme.Set(i%2==0 and 'gatherly' or 'original') end
assert(note.nameInput:GetText()=='Unsaved title' and note.save:IsShown())
A.Theme.Set('original');assert(not note.save.themeNativeButton:IsShown())
assert(note.save.face:IsShown() and note.save.outer:IsShown(),'Original button surfaces must be restored')
assert(note.save.caption:IsShown() and note.save.caption:GetText()=='Save note','Original must restore its own readable caption')
assert(not A.Theme.Set('invalid') and A.db.theme=='original')
A.Theme.Set('gatherly')
local previousTrim=A.mapThemeTrim
local nativeTitle=CreateFrame('Texture');nativeTitle:SetAtlas('NativeBrownTitle')
nativeTitle:SetTexCoord(.1,.2,.1,.8,.9,.2,.9,.8)
A.mapThemeTrim={themeChrome={NineSlice={TopEdge=nativeTitle}}}
local footer=CreateFrame('Frame');local rail=CreateFrame('Frame')
A.Theme.Register(footer,'footer');A.Theme.Register(rail,'rail')
assert(footer.mapperlyBrown.texture=='Interface\\\\DialogFrame\\\\UI-DialogBox-Background' and rail.mapperlyBrown.texture==footer.mapperlyBrown.texture,'bars must tile a brown background instead of stretching NineSlice border art')
assert(#footer.mapperlyBrown.coords==4 and footer.mapperlyBrown.coords[1]==0 and footer.mapperlyBrown.coords[2]==1,'dynamic header border UVs must not be copied into bar backgrounds')
local zone=CreateFrame('FontString');zone:SetFont('OriginalFont.ttf',12,'')
zone.GetFont=function(self) return self.fontPath,self.fontSize,self.fontFlags end
A.Theme.Register(zone,'zone');assert(zone.fontSize==18 and zone.fontFlags=='OUTLINE')
A.Theme.Set('original')
assert(not footer.mapperlyBrown:IsShown() and not rail.mapperlyBrown:IsShown(),'Original must hide new brown materials')
assert(not footer.mapperlyBrownBase:IsShown() and not rail.mapperlyBrownBase:IsShown(),'Original must also hide the brown base fill')
assert(zone.fontPath=='OriginalFont.ttf' and zone.fontSize==12 and zone.fontFlags=='','Original must restore the heading font')
A.mapThemeTrim=previousTrim
UIParent:SetSize(800,600);A.ShowSettings()
assert(settings:GetHeight()*settings.scale<=560.01)
assert(A.themeChoices.original.point[4]+A.themeChoices.original:GetWidth()<=592)
''')
print('PASS: persisted themes, live selector, native chrome/actions, Original restoration and editor state')
