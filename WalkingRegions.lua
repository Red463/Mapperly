local _,A=...
local R={};A.WalkingRegions=R
local values={};local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
for i=1,#alphabet do values[alphabet:byte(i)]=i-1 end
local powers={32,16,8,4,2,1}
function R.Get(p)
    local d=A.WalkingRegionData;local row=d and d.version==1 and d.zones[p.mapID]
    local z=A.Terrain.Zone(p.mapID)
    if not row or not z or row.w~=z.w or row.h~=z.h or row.baseSha256~=z.maskSha256 then return end
    local patch=A.GroundCorrectionData and A.GroundCorrectionData.zones[p.mapID]
    if row.groundCells~=(patch and patch.cells or 0) or row.groundSha256~=(patch and patch.maskSha256 or '') then return end
    if not A.Terrain.Allowed(p) then return 0 end
    local x,y=math.min(z.w-1,math.floor(p.x*z.w)),math.min(z.h-1,math.floor(p.y*z.h))
    for id,region in ipairs(row.exceptions) do
        local dx,dy=x-region.x,y-region.y
        if dx>=0 and dy>=0 and dx<region.w and dy<region.h then
            local line=region.rows[dy+1];local bits=line and values[line:byte(math.floor(dx/6)+1)]
            if bits and math.floor(bits/powers[dx%6+1])%2==1 then return id+1 end
        end
    end
    return 1
end
