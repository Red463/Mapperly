"""Dialog actions use classic red art, textured cards and live captions."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
A.Theme.Set('gatherly');A.ShowNavigationInput(1431);A.ShowNote(1431,.4,.5)
local f=A.navigationWindow
for _,b in ipairs({f.start,f.save,f.preview,f.journey,f.stop,A.noteWindow.save,A.noteWindow.navigate,A.noteWindow.delete,A.themeChoices.gatherly,A.themeChoices.original}) do
 assert(b.themeNativeButton and b.themeNativeButton:IsShown(),'every dialog action must use the classic red button')
end
local card=A.Dialogs.Card(f,0,0,200,100)
assert(card.backdrop.bgFile=='Interface\\\\FrameGeneral\\\\UI-Background-Rock','settings groups must use native textured panels')
assert(card.themeCardBase and card.themeCardBase:IsShown(),'textures must retain an opaque backing')
assert(f.themeWindowBase and f.themeWindowBase:IsShown(),'main dialogs must have an opaque textured base')
local b=A.Dialogs.Action(f,'Before',0,0,100,function() end);b:SetText('After')
assert(b.themeNativeButton.mapperlyCaption:GetText()=='After','dynamic native captions must update without a hover')
b:SetEnabled(false);assert(not b.themeNativeButton:IsEnabled() and b.themeNativeButton.mapperlyCaption.textColor[1]==.5,'disabled actions must look disabled immediately')
b:SetEnabled(true);assert(b.themeNativeButton:IsEnabled() and b.themeNativeButton.mapperlyCaption.textColor[1]==1)
assert(not A.noteWindow.iconButtons.note_enemy.themeNativeButton,'note icon choices must remain quiet')
assert(A.themeChoices.gatherly.themeNativeButton.mapperlySelectedMark:IsShown(),'current theme must remain visibly selected')
A.Theme.Set('original')
assert(not f.save.themeNativeButton:IsShown() and f.save.face:IsShown() and not card.themeCardBase:IsShown())
assert(card.backdrop.bgFile=='Interface\\\\Buttons\\\\WHITE8X8')
A.Theme.Set('gatherly');assert(f.save.themeNativeButton:IsShown() and card.themeCardBase:IsShown())
''')
print('PASS: classic red dialog actions, textured groups, selection, dynamic captions and charcoal restoration')
