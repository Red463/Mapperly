local _,A=...
local R={};A.Roads=R
local floor=math.floor
function R.Strength(value)
    if type(value)~='number' or value~=value or math.abs(value)==math.huge then value=3 end
    local level=math.max(1,math.min(5,floor(value+.5)))
    return level,({'Light','Moderate','Balanced','Firm','Strong'})[level],({1.10,1.20,1.35,1.75,2.50})[level]
end
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local values={};for i=1,#alphabet do values[alphabet:byte(i)]=i-1 end
local powers={32,16,8,4,2,1}
function R.Zone(mapID,terrain)
    local data=A.RoadData
    local z=type(data)=='table' and data.version==1 and type(data.zones)=='table' and data.zones[mapID]
    if type(z)~='table' or type(z.rows)~='table' or not terrain or z.w~=terrain.w or z.h~=terrain.h
        or z.widthYards~=terrain.widthYards or z.heightYards~=terrain.heightYards then return end
    local supplements=A.RoadSupplementData
    local patch=supplements and supplements.version==1 and supplements.build==data.build and supplements.zones[mapID]
    if patch and patch.terrainMaskSha256==terrain.maskSha256 and patch.baseRoadCells==z.roadCells and
        patch.w==z.w and patch.h==z.h and patch.widthYards==z.widthYards and patch.heightYards==z.heightYards and
        type(patch.baseRows)=='table' and #patch.baseRows==#z.rows and type(patch.rows)=='table' and #patch.rows==z.h then
        local matches=true
        for i,row in ipairs(z.rows) do if row~=patch.baseRows[i] then matches=false;break end end
        if matches then z=patch end
    end
    if z.roadCells==0 then return end
    return z
end
function R.Cell(z,x,y)
    if x<0 or y<0 or x>=z.w or y>=z.h then return false end
    local row=z.rows[y+1]
    local n=type(row)=='string' and values[row:byte(floor(x/6)+1)]
    return n and floor(n/powers[x%6+1])%2==1 or false
end
