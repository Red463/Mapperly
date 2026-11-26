"""Illustrated service categories retain exact providers, examples, search and proximity."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('A = {}')
lua.execute('assert(loadstring(...))("Mapperly", A)', (root/'NearbyServiceGroups.lua').read_text(encoding='utf8'))
lua.execute("""
local G = A.NearbyServiceGroups
local near = {npcID=1, key='s1', name='Dalmond', detail='General Goods', distance=5, category='vendor'}
local far = {npcID=2, key='s2', name='Kyndri', detail='Innkeeper', distance=60, category='vendor'}
local other = {key='s3', name='Kroka', detail='Travelling merchant', distance=100, category='vendor'}
local journeyman = {key='t1', name='Blackbar', detail='Journeyman Blacksmith', distance=7}
local master = {key='t2', name='Futhark', detail='Master Blacksmith', distance=24}
local inn = {key='s2', name='Kyndri', detail='Innkeeper', distance=60}
local mail = {key='m1', name='Mailbox', detail='Mailbox', distance=19}
local snapshot = {vendor={near,far,other}, repair={}, trainer={journeyman,master}, inn={inn}, flight={}, mail={mail}}
local reason
A.NearbyServices = {ListByRole=function() return snapshot, 'Darkshore', reason end}
A.VendorGoods = {
  stock={[1]={5,7,9,11,15}, [2]={5,8,10,12}},
  items={[5]={'food','Tough Jerky',555},[7]={'arrows','Sharp Arrow',777},[9]={'supplies','Linen Thread'},
         [8]={'food','Moist Cornbread',888},[10]={'drink','Melon Juice',1010},
         [11]={'reagents','Sacred Candle',111},[12]={'bags','Brown Leather Satchel',1212},
         [15]={'bullets','Heavy Shot',1515}},
}
local groups,zone = G.List()
assert(zone=='Darkshore' and #groups==4)
assert(groups==G.List('  '),'stationary list changes identity')
assert(groups[1].key=='vendor' and groups[2].key=='trainer' and groups[3].key=='inn' and groups[4].key=='mail')
local cats=groups[1].categories
local expected={'arrows','bullets','food','drink','bags','supplies','reagents','unlisted'}
for i,key in ipairs(expected) do assert(cats[i].key=='vendor:'..key,'unexpected order '..cats[i].key) end
local food=cats[3]
assert(#food.providers==2 and food.providers[1].service==near and food.providers[2].service==far)
assert(food.providers[1].example=='Tough Jerky' and food.providers[1].icon==555)
assert(cats[6].providers[1].icon:find('Interface',1,true),'item without art needs category art')
assert(cats[8].providers[1].service==other,'unknown/discovered vendor became unreachable')
local trainer=groups[2].categories[1]
assert(#groups[2].categories==1 and trainer.label=='Blacksmithing' and #trainer.providers==2)
assert(trainer.icon==136241 and trainer.providers[2].example=='Master Blacksmith')
assert(groups[3].categories[1].providers[1].service==inn,'multi-role service lost in Innkeepers')
assert(groups[4].categories[1].providers[1].service==mail)
local found=G.List('  kYnDRi  moIST  ')[1].categories[1]
assert(found.key=='vendor:food' and #found.providers==1 and found.providers[1].service==far)
assert(found.providers[1].example=='Moist Cornbread' and found.providers[1].icon==888)
assert(found.providers[1].subtitle:find('Kyndri',1,true))
assert(#G.List('Dalmond moist')==0,'do not mix separate NPCs when matching multiple terms')
assert(#G.List('no such item')==0 and #G.List('%[')==0,'use literal text')
assert(G.List('master blacksmith')[1].categories[1].providers[1].service==master)
local possible=G.List('kroka')
assert(#possible==1 and possible[1].categories[1].providers[1].service==other)
-- Real snapshots are recreated and ordered from the current player position after a move.
local previous=snapshot
far.distance=3
snapshot={vendor={far,near,other},repair={},trainer=previous.trainer,inn=previous.inn,flight={},mail={mail}}
assert(G.List('food')[1].categories[1].providers[1].service==far)
snapshot=nil; reason='Player position is unavailable.'
local missing,_,why=G.List()
assert(#missing==0 and why==reason)
""")
print("PASS: stable illustrated groups, nearest provider, trainer ranks, fallback merchants and actual stock search")
