"""Native movable state may be reset independently of Mapperly's lock setting."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(r/'tests/run.py'))['lua']
l.execute('''
local f=A.map;local combat=false;local movable=false;local moves=0
InCombatLockdown=function()return combat end
f.IsProtected=function()return false end
f.SetMovable=function(_,v)movable=v end
f.IsMovable=function()return movable end
f.StartMoving=function()
 assert(movable,'WorldMapFrame:StartMoving(): Frame is not movable')
 moves=moves+1
end
for _,theme in ipairs({'gatherly','original'})do
 for _,compact in ipairs({true,false})do
  for _,inCombat in ipairs({false,true})do
   combat=false;A.db.locked=false;A.db.compact=compact;A.Theme.Set(theme)
   combat=inCombat;movable=false;local before=moves
   local ok,why=pcall(A.bar:GetScript('OnDragStart'),A.bar,'LeftButton')
   assert(ok,'drag must repair native movable state without raising: '..tostring(why))
   assert(movable and moves==before+1 and A.dragging,'unlocked native frame must become movable before StartMoving')
   A.bar:GetScript('OnDragStop')(A.bar);assert(not A.dragging)
  end
 end
end
-- External restrictions or unexpected native failures must not strand guards.
combat=false;A.db.locked=false
f.StartMoving=function()A.ApplyLayout(true);error('native movement refused')end
assert(pcall(A.bar:GetScript('OnDragStart'),A.bar),'a rejected start must not escape the drag handler')
assert(not A.dragging and not A.dragLayoutPending,'failed starts must release deferred-layout guards')
local before=moves
f.StartMoving=function()moves=moves+1 end
f.SetMovable=function()movable=false end
movable=false
assert(pcall(A.bar:GetScript('OnDragStart'),A.bar))
assert(not A.dragging and moves==before,'do not call StartMoving if another addon refuses movable state')
A.db.locked=true
f.SetMovable=function()error('locked frame must not be changed')end
assert(pcall(A.bar:GetScript('OnDragStart'),A.bar)and not A.dragging)
A.db.locked=false;combat=true;f.IsProtected=function()return true end
assert(pcall(A.bar:GetScript('OnDragStart'),A.bar)and not A.dragging,'retain protected-frame combat guard')
''')
print('PASS: repair reset native movable state, both sizes/themes/combat states, failed-start cleanup and lock/protected guards')
