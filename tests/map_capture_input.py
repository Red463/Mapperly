"""Diagnostic capture must not turn decorative map trim into a mouse blocker."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/run.py'))['lua']
lua.execute('''
InCombatLockdown=function()return false end
A.db.locked=false
local R,f,bar,trim=A.MapReport,A.map,A.bar,A.mapThemeTrim
assert(trim and trim.mouse==false and bar.mouse==true)
-- Native widget behavior missing from the basic frame double: installing a
-- previously absent mouse script enables input, including through HookScript.
for _,frame in ipairs({f,bar,trim})do
 local hook=frame.HookScript
 frame.HookScript=function(self,script,fn)
  local absent=not self:GetScript(script)
  hook(self,script,fn)
  if absent and (script=='OnMouseDown'or script=='OnMouseUp')then self:EnableMouse(true)end
 end
end
local moves=0
f.StartMoving=function()moves=moves+1 end
-- The HIGH trim covers the whole map above the title bar. It must remain
-- input-transparent so native hit testing delivers a drag to the title bar.
local function drag()
 local target=trim.mouse and trim or bar
 local handler=target:GetScript('OnDragStart')
 if handler then handler(target,'LeftButton')end
 if target==bar then bar:GetScript('OnDragStop')(bar)end
end
drag();assert(moves==1,'baseline drag must reach the title bar')
SlashCmdList.MAPPERLY('mapreport start')
drag();assert(moves==2,'starting map diagnostics must not block title-bar dragging')
assert(trim.mouse==false,'capture must not enable mouse input on decorative trim')
trim.IsMouseEnabled=function(self)return self.mouse end
assert(R.Build():find('Map trim:',1,true)and R.Build():find('mouse=false',1,true),'reports must expose trim input state')
R.Stop();drag();assert(moves==3,'stopping capture must leave input unchanged')
for _,theme in ipairs({'original','gatherly'})do
 A.Theme.Set(theme);R.Start();local n=moves;drag()
 assert(moves==n+1 and not trim.mouse,'both themes must retain drag input during capture')
 assert(R.Build():find('bar.OnDragStart',1,true),'drag diagnostics must still be recorded')
 R.Stop()
end
''')
print('PASS: capture preserves decorative input transparency and title-bar dragging in both themes')
