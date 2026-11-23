"""Saved road strength must change planning, cache identity and settings."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/roads.py'))['lua']
lua.execute('''
assert(A.InitStore({}).roadPreferenceStrength==3,'existing behaviour must remain the default')
assert(A.InitStore({roadPreferenceStrength=99}).roadPreferenceStrength==5)
assert(A.InitStore({roadPreferenceStrength=0/0}).roadPreferenceStrength==3)
assert(A.InitStore({roadPreferenceStrength=1}).roadPreferenceStrength==1)
assert(A.Roads.Strength(3)==3)
local z=A.TerrainData.zones[1429]
local a={mapID=1429,x=.825,y=.686}
local b={mapID=1429,x=.42265799844097,y=.665577526985558,name='Road strength'}
local light=assert(A.Journey.Plan(a,b,{preferRoads=true,roadPreferenceStrength=1}))
local strong=assert(A.Journey.Plan(a,b,{preferRoads=true,roadPreferenceStrength=5}))
assert(strong.distance>light.distance+1,'strong preference must accept a longer native road detour')
local again=assert(A.Journey.Plan(a,b,{preferRoads=true,roadPreferenceStrength=1}))
assert(math.abs(again.distance-light.distance)<.0001,'strength changes cannot reuse another strength cache')
assert(A.Terrain.Validate(strong) and A.Terrain.Validate(light))
A.InitStore({preferRoads=true,roadPreferenceStrength=5})
assert(math.abs(assert(A.Journey.Plan(a,b,{})).distance-strong.distance)<.0001,'saved strength must reach local planning')
local old=A.TravelNetwork
A.TravelNetwork={Canonical=function(v) return v end,Plan=function(_,_,o) assert(o.roadPreferenceStrength==5);return {propagated=true} end}
local other=assert(A.Terrain.Approach({mapID=1431,x=.77,y=.44},30))
assert(A.Journey.Plan(a,other,{}).propagated,'cross-zone planning must receive saved strength')
A.TravelNetwork=old
''')
ui=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
ui.execute('''
A.Navigation.Stop()
local slider=A.roadStrengthSlider;assert(slider,'navigation settings must expose road strength')
A.Navigation.SetSmartRouting(true);A.Navigation.SetPreferRoads(true)
assert(slider:IsEnabled())
slider:SetValue(5)
assert(A.db.roadPreferenceStrength==5 and slider.valueText:GetText():find('Strong',1,true))
A.Navigation.SetPreferRoads(false)
assert(not slider:IsEnabled() and A.db.roadPreferenceStrength==5)
A.Navigation.SetPreferRoads(true);A.Navigation.SetSmartRouting(false)
assert(not slider:IsEnabled())
A.Navigation.SetSmartRouting(true)
assert(slider:IsEnabled() and A.db.roadPreferenceStrength==5)
local oldStart=A.Navigation.Start;local count=0
A.Navigation.pending={map=1431,x=.4,y=.6,name='Pending road target'}
A.Navigation.Start=function(map,x,y,name,options)
 count=count+1;assert(map==1431 and x==40 and y==60 and name=='Pending road target' and options.mode=='terrain')
 assert(A.db.roadPreferenceStrength==2);return true
end
A.Navigation.SetRoadPreferenceStrength(2)
assert(count==1,'changing strength must replan the pending destination')
A.Navigation.SetRoadPreferenceStrength(2)
assert(count==1,'selecting the same strength cannot restart planning')
A.Navigation.Start=oldStart;A.Navigation.Stop()
''')
print('PASS: road strength persistence, actual route differences, cache separation, network propagation and settings states')
