"""Persistent destination and richer note contracts, independent of UI mocks."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('A={}; C_Map={GetMapInfo=function(id) return {name="Zone "..id} end}')
for name in ['Store.lua','Destinations.lua']:
    path=root/name
    if path.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',path.read_text(encoding='utf-8-sig'))
lua.execute('''
A.InitStore({})
local D=A.Destinations
assert(D,'destination storage must exist')
local p={map=1431,x=.4256,y=.5124,name='Darkshire'}
assert(D.Save(p));assert(#A.db.savedDestinations==1)
p.name='Changed outside';assert(A.db.savedDestinations[1].name=='Darkshire','save must copy the record')
assert(D.Save({map=1431,x=.4256,y=.5124,name='Renamed'}))
assert(#A.db.savedDestinations==1 and A.db.savedDestinations[1].name=='Renamed')
assert(not D.Save({map=1431,x=math.huge,y=.5,name='Invalid'}))
assert(not D.Save({map=1.5,x=.1,y=.2,name='Invalid map'}))
for i=1,25 do D.Remember({map=1431,x=i/100,y=.5,name='Stop '..i}) end
assert(#A.db.destinationHistory==20 and A.db.destinationHistory[1].name=='Stop 25')
D.Remember({map=1431,x=.1,y=.5,name='Visit again'})
assert(#A.db.destinationHistory==20 and A.db.destinationHistory[1].name=='Visit again')
local saved=A.db.savedDestinations[1]
assert(D.Remove(saved));assert(#A.db.savedDestinations==0)
D.ClearHistory();assert(#A.db.destinationHistory==0)
local legacy={map=1431,x=.5,y=.4,name='Old note',category='notes'}
local db=A.InitStore({notes={legacy},savedDestinations={false,{map=0/0,x=.1,y=.2,name='bad'},p},destinationHistory='bad'})
assert(#db.savedDestinations==1 and #db.destinationHistory==0)
assert(db.notes[1]==legacy,'existing note identity must survive migration')
assert(A.UpdateNote(legacy,{name='Camp',description='Meet by the fire',icon='inn',group='Friends'}))
assert(legacy.description=='Meet by the fire' and legacy.icon=='inn' and legacy.group=='Friends')
assert(not A.UpdateNote(legacy,{name='  ',description='Lose this'}))
assert(legacy.name=='Camp' and legacy.description=='Meet by the fire','invalid edit must be atomic')
local note=A.AddNote(1431,.2,.3,'Ore',{description='Rich vein',icon='unknown',group='Mining'})
assert(note and note.icon=='notes' and note.group=='Mining')
assert(A.RemoveNote(note) and not A.RemoveNote(note))
assert(A.ValidPin({map=1/0,x=.1,y=.2,name='bad'})==false)
local corrupt={map=1431,x=.2,y=.3,name='Legacy',category='notes',description=true,group=42,icon={}}
assert(A.InitStore({notes={false,corrupt}}).notes[1]==corrupt)
assert(corrupt.description=='' and corrupt.group=='' and corrupt.icon=='notes','new optional note fields must recover from invalid saved values')
local missing={map=1431,x=.2,y=.3,name='Old camp',description={},group={}}
assert(A.InitStore({notes={missing}}).notes[1]==missing)
assert(missing.category=='notes' and missing.group=='' and missing.description=='','legacy notes without a category must recover safely')
local a={map=1431,x=.1,y=.2,name='A'};local b={map=1431,x=.3,y=.4,name='B'}
db=A.InitStore({savedDestinations={[1]=a,[3]=b},notes={[1]=missing,[3]=corrupt}})
assert(#db.savedDestinations==2 and #db.notes==2,'holes must not discard later records on reload')
local original=db.savedDestinations[1]
assert(D.Update(original,{map=1416,x=.6,y=.7,name='Moved'}))
assert(#db.savedDestinations==2 and db.savedDestinations[1].map==1416,'coordinate edits must replace the original saved record')
assert(not D.Update(original,a),'stale record references must not create an extra destination')
for _,key in ipairs(A.noteIcons) do
 local note=A.AddNote(1431,.4,.5,key,{icon=key})
 assert(note.icon==key)
 A.InitStore(A.db);assert(note.icon==key,'new icons must survive reload')
end
local old=A.AddNote(1431,.4,.5,'Legacy',{icon='inn'});A.InitStore(A.db)
assert(old.icon=='inn','older saved icon choices must stay intact')
''')
print('PASS: persistent destinations, bounded history, migration and atomic note editing')
