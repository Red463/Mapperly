-- Published reference facts, checked 2026-11-24; not verified server requirements.
-- Source and exceptions: Data/FishingLevels-SOURCES.md. No addon dependency.
local _,A=...
local maps={}
local function band(minimum,recommended,ids)
    for _,id in ipairs(ids) do maps[id]={minimum=minimum,recommended=recommended} end
end
band(1,25,{1426,1429,1411,1420,1438,1412})
band(1,75,{1413,1432,1436,1421,1439,1453,1454,1455,1456,1457,1458})
band(51,150,{1431,1437,1433,1424,1440,1442})
band(126,225,{1435,1445,1434,1416,1417,1441,1443})
band(201,300,{1447,1422,1425,1444,1448,1446,1449,1450})
band(326,425,{1430,1428,1423,1452,1451})
-- A zone map covers several waters: retain the published higher thresholds.
maps[1434].maximum=201;maps[1434].recommendedMaximum=300
maps[1434].waters='Jaguero Isle: minimum 201; recommended 300.'
maps[1444].maximum=326;maps[1444].recommendedMaximum=425
maps[1444].waters='Jademir Lake: minimum 326; recommended 425.'
maps[1447].maximum=326;maps[1447].recommendedMaximum=425
maps[1447].waters="Hetaera's Clutch, Bay of Storms and Scalebeard's Cave: minimum 326; recommended 425."
A.FishingLevelsData={maps=maps,checked='2026-11-24',source='WCLBox Forever fishing reference'}
