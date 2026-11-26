"""Service browsing lives in the map drawer. The remaining destination tabs fit both themes."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(root/'tests/run.py'))['lua']
lua.execute("""
A.ShowNavigationInput(1431)
local f=A.navigationWindow
assert(not f.tabs.services and not f.servicePage)
for _,theme in ipairs({'gatherly','original'}) do
    A.db.theme=theme
    A.Theme.Apply()
    local right=0
    for _,page in ipairs({'entry','saved','recent','quests'}) do
        local tab=f.tabs[page]
        assert(tab and tab:IsShown() and tab.point[4]>right)
        right=tab.point[4]+tab:GetWidth()
        assert(right<=f:GetWidth()-8)
        tab:GetScript('OnClick')()
        assert(f.page==page)
    end
end
""")
print('PASS: four usable destination tabs in both themes')
