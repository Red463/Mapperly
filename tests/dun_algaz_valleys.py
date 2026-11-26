"""Dun Algaz's three open-air valleys connect successive gates on dry ground."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benchmark_route_matrix import runtime

lua = runtime(profile='firm')
lua.execute("""
local map=1437
local zone=A.Terrain.Zone(map)
local correction=A.GroundCorrectionData.zones[map]
assert(correction and correction.cells==2110, 'Missing audited Dun Algaz ground components')
assert(correction.baseSha256==zone.maskSha256)
local region=A.WalkingRegionData.zones[map]
assert(region.groundSha256==correction.maskSha256)
local water=A.Water.Zone(map,zone)
assert(water, 'Wetlands native water mask missing')
local original=A.TerrainData.zones[map]
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function bit(rows,x,y)
    local byte=(rows[y+1] or ''):sub(math.floor(x/6)+1,math.floor(x/6)+1)
    if #byte==0 then return false end
    local index=assert(alphabet:find(byte,1,true))-1
    return math.floor(index/2^(5-x%6))%2==1
end
local count=0
for y=0,zone.h-1 do
    for x=0,zone.w-1 do
        if bit(correction.rows,x,y) then
            count=count+1
            assert(not bit(original.rows,x,y) and A.Water.Cell(water,x,y),
                   'Each restored cell must be previously restricted and native-dry')
        end
    end
end
assert(count==correction.cells)
local gates=A.StructureData.corridors
local valleys={
    {gates[68443158].b,gates[68441769].a},
    {gates[68441769].b,gates[126354].a},
    {gates[126354].b,gates[73025].a},
}
local distinct={[1]=true}
for _,v in ipairs(valleys) do
    assert(v[1].mapID==map and v[2].mapID==map)
    local id=A.WalkingRegions.Get(v[1])
    assert(id and id>1 and not distinct[id] and id==A.WalkingRegions.Get(v[2]),
           'Outdoor valley must connect its two mouths only')
    distinct[id]=true
    local options={preferRoads=true,roadPreferenceStrength=4,allowSwimming=false}
    local path,reason=A.Terrain.Path(v[1],v[2],options)
    assert(path,reason)
    assert(A.Terrain.Validate({points=path},options))
    for strength=0,5 do
        local allowed={preferRoads=strength>0,roadPreferenceStrength=strength,allowSwimming=true}
        local before=A.PathReuse.Stats().bakedHits
        local baked=assert(A.Terrain.Path(v[1],v[2],allowed))
        assert(A.PathReuse.Stats().bakedHits==before+1, 'Outdoor tunnel handoff should use baked path')
        assert(A.Terrain.Validate({points=baked},allowed))
    end
end
""")
print('PASS: 2,110 dry-only restored Wetlands cells, three separate traversable valleys')
