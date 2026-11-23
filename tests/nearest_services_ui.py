"""Services tab retains both themes, existing tabs, source guards and walking intent."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute("""
A.Navigation.Stop();A.db.navigationMode='terrain';A.ShowNavigationInput(1431)
local f=A.navigationWindow;assert(f.tabs.services,'Destinations needs a Services tab')
f.SelectPage('services');local u=f.serviceUI
assert(f.servicePage:IsShown() and not f.questPage:IsShown() and not f.entryPage:IsShown())
for _,tab in pairs(f.tabs) do assert(tab.point[4]+tab:GetWidth()<=f:GetWidth()-24,'five tabs must fit without clipping') end
local originalRequest,originalResolve=A.NearestServices.Request,A.NearestServices.Resolve
local callback,failed
A.NearestServices.Request=function(kind,done,fail) assert(kind=='inn');callback=done;failed=fail;return true end
local pin={map=1431,x=.74,y=.44,name='Innkeeper',category='inn',serviceKey='fixture',serviceKind='inn',walkingOnly=true,source='Snapshot',serviceExact={map=1431,x=.74,y=.44,name='Innkeeper'}}
u.find:GetScript('OnClick')(u.find)
assert(u.busy and not u.result)
callback({pin=pin,plan={kind='walking',distance=200,points={},legs={}},complete=true,checked=2,total=5})
assert(not u.busy and u.result and u.list.rows[1].record.pin.serviceKey=='fixture')
assert(u.summary:GetText():find('Nearest verified',1,true))
local previewed,went=0,0;local preview,go=A.JourneyView.Preview,A.Navigation.ToPin
A.NearestServices.Resolve=function(p)return p end
A.JourneyView.Preview=function(p)assert(p.walkingOnly);previewed=previewed+1;return true end
A.Navigation.ToPin=function(p)assert(p.walkingOnly);went=went+1;return true end
local row=u.list.rows[1];row.preview:GetScript('OnClick')(row.preview);assert(previewed==1)
A.NearestServices.Resolve=function()return nil,'Service changed' end
row.go:GetScript('OnClick')(row.go);assert(went==0 and f.status:GetText()=='Service changed','stale service cannot start navigation')
A.NearestServices.Resolve=function(p)return p end
row.go:GetScript('OnClick')(row.go);assert(went==1 and not f:IsShown())
A.ShowNavigationInput(1431);f.SelectPage('services');u.find:GetScript('OnClick')(u.find)
callback({pin=pin,plan={kind='walking',distance=200},complete=false,checked=12,total=50})
assert(u.summary:GetText():find('Best found',1,true),'partial result must not claim proven nearest')
for _,theme in ipairs({'gatherly','original'}) do A.db.theme=theme;A.Theme.Apply();assert(f.tabs.services:IsShown()) end
f.SelectPage('quests');assert(not f.servicePage:IsShown() and f.questPage:IsShown())
A.JourneyView.Preview=preview;A.Navigation.ToPin=go;A.NearestServices.Request=originalRequest;A.NearestServices.Resolve=originalResolve
""")
print('PASS: Services tab, five-tab layout, themed rows, explicit partial results and stale guarded Preview/Go')
