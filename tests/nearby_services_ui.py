"""Exercise the illustrated drawer through filtering, disclosure, movement and scrolling."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(root / 'tests/run.py'))['lua']
lua.execute("""
A.db.collapsedServiceSections = {}
local function provider(key, name, distance, category, example)
    return {service={key=key, name=name, detail=category, distance=distance, category=category},
        example=example, subtitle=name..' - '..example, icon=12345}
end
local a=provider('npc:1', 'Kyndri', 45, 'vendor', 'Moist Cornbread')
local b=provider('npc:2', 'Dellylah', 88, 'vendor', 'Spiced Bread')
local c=provider('npc:3', 'Tannysa', 302, 'trainer', 'Herbalism')
local food={key='vendor:food', label='Food', icon=12345, providers={a,b}}
local trade={key='vendor:trade', label='Trade supplies', icon=456, providers={b}}
local trainer={key='trainer:herb', label='Herbalism', icon=789, providers={c}}
local vendor={key='vendor',label='Vendors',categories={food,trade}}
local trainers={key='trainer',label='Trainers',categories={trainer}}
local all={vendor, trainers}
local calls, reason, query, navigated, routeCalls, rejects = 0, nil, nil, nil, 0, false
A.NearbyServiceGroups = {List=function(q)
    calls=calls+1
    query=q
    if reason then return {}, nil, reason end
    if q=='bread' then return {{key='vendor', label='Vendors', categories={food}}}, 'Darkshore' end
    if q~='' then return {}, 'Darkshore' end
    return all, 'Darkshore'
end}
GetSubZoneText=function() return 'Auberdine' end
A.NearbyServices.Navigate=function(service)
    if rejects then return nil, 'Location unavailable.' end
    navigated, routeCalls=service.key, routeCalls+1
    return true
end
local p=A.CreateNearbyServicesPanel(WorldMapFrame)
p.scroll:SetHeight(390)
p.scroll:SetWidth(286)
local function visible(pool, key)
    for _,btn in ipairs(pool) do
        if btn:IsShown() and btn.line and btn.line.key==key then return btn end
    end
end
local function click(button) assert(button);button:GetScript('OnClick')(button) end
local function search(q)
    p.search:SetText(q)
    p.search:GetScript('OnTextChanged')(p.search, true)
end
assert(not p:IsShown() and calls==0)
p:Show()
assert(query=='' and p.place:GetText()=='Auberdine, Darkshore' and p.search.template=='SearchBoxTemplate')
local vh=visible(p.headers, 'vendor')
assert(vh and vh.count:GetText()=='2' and visible(p.headers,'trainer'))
local row=visible(p.rows,food.key)
assert(row.title:GetText()=='Food' and row.detail:GetText()==a.subtitle and row.icon.texture==12345)
assert(row.distance:GetText()=='45 yd' and row.more:IsShown())
click(row)
assert(navigated=='npc:1')
click(row.more)
local alternative=visible(p.rows,food.key..'/'..b.service.key)
assert(alternative and alternative.title:GetText()=='Dellylah')
click(alternative)
assert(navigated=='npc:2')
click(vh)
assert(A.db.collapsedServiceSections.vendor and not visible(p.rows,food.key) and visible(p.rows,trainer.key))
search('bread')
assert(query=='bread' and visible(p.rows,food.key) and not visible(p.headers,'trainer'))
assert(A.db.collapsedServiceSections.vendor,'search must not erase a saved collapse')
search('')
assert(not visible(p.rows,food.key))
click(visible(p.headers,'vendor'))
row=visible(p.rows,food.key)
row:GetScript('OnMouseDown')(row)
food.providers={b,a}
all={vendor,trainers}
p:GetScript('OnUpdate')(p,1.01)
click(row)
assert(navigated=='npc:2' and routeCalls==2,'recycling must not retarget a held click')
rejects=true;click(row)
assert(p.status:GetText()=='Location unavailable.')
search('missing')
assert(p.empty:IsShown() and not visible(p.headers,'vendor'))
reason='Player position is unavailable.'
p:GetScript('OnUpdate')(p,1.01)
assert(p.empty:GetText()==reason)
reason=nil
local categories={}
for i=1,60 do
    categories[i]={key='vendor:'..i,label='Goods '..i,icon=12345, providers={a}}
end
all={{key='vendor',label='Vendors',categories=categories}}
p.scroll:SetHeight(85)
search('')
local maximum=p.content:GetHeight()-85
p.scroll:SetVerticalScroll(maximum)
p.scroll:GetScript('OnVerticalScroll')(p.scroll,maximum)
assert(#p.rows<10 and visible(p.rows,'vendor:60'),'long lists must recycle rows through the last entry')
p:Hide()
p:Show()
assert(p.scroll:GetVerticalScroll()==0 and visible(p.headers,'vendor'))
""")
print('PASS: illustrated drawer, service disclosure, category alternatives, search, scrolling and exact clicks')
