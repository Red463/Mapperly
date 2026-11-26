"""Destination library and note editor interaction contracts."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text(encoding='utf-8'))
lua.execute('''
fakeUI();A={};C_Map={GetMapInfo=function(id) return {name='Zone '..id} end}
local create=CreateFrame
CreateFrame=function(kind,...) local f=create(kind,...);if kind=='FontString' then f.GetStringWidth=function(self) return #self:GetText()*7 end end;return f end
A.map=WorldMapFrame;A.Print=function() end;A.Refresh=function() end
LibStub=function() return {GetWorldCoordinatesFromZone=function(_,x,y,map) return x*1000,y*1000,0 end,GetPlayerWorldPosition=function() return 0,0,0 end} end
GetPlayerFacing=function() return 0 end
''')
for name in ['Store.lua','Theme.lua','Destinations.lua','Buttons.lua','Pins.lua','Navigation.lua','Dialogs.lua','NavigationUI.lua','NotesUI.lua']:
    path=root/name
    if path.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',path.read_text(encoding='utf-8-sig'))
lua.execute('''
A.RefreshPins=function() end
A.InitStore({})
A.ShowNavigationInput(1431)
local f=A.navigationWindow
assert(f.savedTab and f.recentTab,'destination window needs Saved and Recent tabs')
assert(f:GetWidth()==333 and f:GetHeight()<=345 and f.scale==1,'destination entry uses the native tool width')
f.nameInput:SetText('Home');f.xInput:SetText('42.56');f.yInput:SetText('51.24')
f.save:GetScript('OnClick')()
assert(#A.db.savedDestinations==1 and not A.Navigation.target,'saving must not start navigation')
f.savedTab:GetScript('OnClick')()
assert(f.library.rows[1].record.name=='Home')
local row=f.library.rows[1]
assert(row.go.point[4]>=row.open.point[4]+row.open:GetWidth() and row.remove.point[4]>=row.go.point[4]+row.go:GetWidth())
assert(row.remove.point[4]+row.remove:GetWidth()<=row:GetWidth() and -row.remove.point[5]+row.remove:GetHeight()<=row:GetHeight())
local savedListHeight=f.library.frame:GetHeight()
f:FitToolHeight(f:GetHeight()+100)
assert(f.library.frame:GetHeight()==savedListHeight+100,'tall drawers give spare height to their lists')
f:FitToolHeight(f:GetHeight())
f.library.rows[1].open:GetScript('OnClick')();f.xInput:SetText('43.56');f.save:GetScript('OnClick')()
assert(#A.db.savedDestinations==1 and math.abs(A.db.savedDestinations[1].x-.4356)<1e-12,'editing saved coordinates must replace the original')
f.xInput:SetText('42.56');f.save:GetScript('OnClick')();f.savedTab:GetScript('OnClick')()
f.library.rows[1].go:GetScript('OnClick')()
assert(A.Navigation.target.name=='Home' and A.Navigation.target.map==1431)
assert(not f:IsShown() and #A.db.destinationHistory==1)
A.ShowNavigationInput(1416);f.recentTab:GetScript('OnClick')()
assert(f.library.rows[1].record.map==1431,'recent destinations must retain their own map')
f.library.rows[1].open:GetScript('OnClick')()
assert(f.targetMap==1431 and f.xInput:GetText()=='42.56')
f.savedTab:GetScript('OnClick')();f.library.rows[1].remove:GetScript('OnClick')()
assert(#A.db.savedDestinations==0 and #A.db.destinationHistory==1)
f.recentTab:GetScript('OnClick')();f.clear:GetScript('OnClick')()
assert(#A.db.destinationHistory==0)
A.ShowNote(1431,.2,.3)
local n=A.noteWindow
assert(n and n.nameInput and n.descriptionInput and n.groupInput and n.iconButtons,'notes need a dedicated styled editor')
n.nameInput:SetText('Camp');n.descriptionInput:SetText('Meet at dusk');n.groupInput:SetText('Friends')
n.iconButtons.note_enemy:GetScript('OnClick')()
assert(n:GetWidth()==333 and n:GetHeight()<=345 and n.scale==1)
n.browserTab:GetScript('OnClick')()
assert(not n.save:IsVisible() and n.browser:IsVisible())
local libraryHeight=n.library.frame:GetHeight()
n:SetHeight(n.toolHeight+80);n:FitToolHeight(n:GetHeight())
assert(n.library.frame:GetHeight()==libraryHeight+80)
n.tabs.edit:GetScript('OnClick')()
assert(n.nameInput:GetText()=='Camp' and n.groupInput:GetText()=='Friends')
assert(n.descriptionInput:GetText()=='Meet at dusk' and n.selectedIcon=='note_enemy')
n:SetHeight(n.toolHeight);n:FitToolHeight(n.toolHeight)
assert(n.library.frame:GetHeight()==libraryHeight and n.save:IsVisible())
n.save:GetScript('OnClick')()
assert(#A.db.notes==1 and A.db.notes[1].description=='Meet at dusk' and A.db.notes[1].icon=='note_enemy')
assert(#A.noteIcons==12,'new note picker must offer twelve purpose-made symbols')
for _,key in ipairs(A.noteIcons) do
 local b=n.iconButtons[key];assert(b,'every note icon must be selectable')
 assert(b.point[4]+b:GetWidth()<=n.editor:GetWidth()-16,'icon choices must fit inside the editor')
end
local p=A.db.notes[1]
A.ShowNote(p.map,p.x,p.y,p)
n.nameInput:SetText('');n.save:GetScript('OnClick')()
assert(n:IsShown() and p.name=='Camp','blank edits must not damage an existing note')
n.nameInput:SetText('New camp');n.save:GetScript('OnClick')()
assert(#A.db.notes==1 and p.name=='New camp','editing must not create duplicates')
A.ShowNote(p.map,p.x,p.y,p);n.navigate:GetScript('OnClick')()
assert(A.Navigation.target.name=='New camp')
A.ShowNote(p.map,p.x,p.y,p);n.browserTab:GetScript('OnClick')()
assert(n.library.rows[1].record==p)
for _,query in ipairs({'absent', 'new camp', 'FRIENDS', 'at dusk', 'zone 1431'}) do
 n.search:SetText(query);n.search:GetScript('OnTextChanged')(n.search)
 assert(n.library.rows[1]:IsShown()==(query~='absent'))
end
n.library.rows[1].open:GetScript('OnClick')()
assert(n.editing==p and n.groupInput:GetText()=='Friends')
n.delete:GetScript('OnClick')();assert(#A.db.notes==0 and not n:IsShown())
A.ShowNote(1416,.4,.5);n.nameInput:SetText('Cancel');n.nameInput:GetScript('OnEscapePressed')()
assert(not n:IsShown() and #A.db.notes==0)
UIParent:SetSize(800,600);A.ShowNavigationInput(1416);A.ShowNote(1416,.1,.2)
assert(f:GetWidth()*f.scale<=760 and f:GetHeight()*f.scale<=560)
assert(n:GetWidth()*n.scale<=760 and n:GetHeight()*n.scale<=560)
''')
print('PASS: saved/recent actions, captured maps, styled notes, editing, icons, deletion and small-screen fit')
