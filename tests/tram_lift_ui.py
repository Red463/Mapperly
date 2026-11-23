"""Independent default-on tram/lift choices and concise route-step labels."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
assert(A.db.useTrams and A.db.useLifts,'new travel preferences must default on')
assert(A.tramsCheck and A.liftsCheck,'each method needs a dedicated navigation setting')
assert(A.tramsCheck:IsEnabled() and A.liftsCheck:IsEnabled(),'bundled tram and Great Lift must be configurable without recording')
A.Journey.Clear();A.Navigation.target=nil;A.Navigation.pending=nil
A.tramsCheck:SetChecked(false);A.tramsCheck:GetScript('OnClick')(A.tramsCheck)
assert(A.db.useTrams==false and A.db.useLifts==true,'tram preference must be independent')
A.liftsCheck:SetChecked(false);A.liftsCheck:GetScript('OnClick')(A.liftsCheck)
assert(A.db.useLifts==false)
A.InitStore({useTrams=false,useLifts=false});A.NavigationSettings.Sync()
assert(not A.tramsCheck:GetChecked() and not A.liftsCheck:GetChecked(),'explicit choices survive initialization')
local text,category=A.RouteSteps.Describe({kind='transport',transport={kind='tram',toName='Ironforge'}})
assert(text=='Tram to Ironforge' and category,'tram steps need an explicit method')
text,category=A.RouteSteps.Describe({kind='transport',transport={kind='lift',toName='Thousand Needles'}})
assert(text=='Lift to Thousand Needles' and category,'lift steps need an explicit method')
''')
print('PASS: independent saved tram/lift choices and route-step labels')
