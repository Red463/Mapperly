local _,A=...
local S={};A.Structures=S
local function same(a,b) return a and b and a.mapID==b.mapID and math.abs(a.x-b.x)<1e-10 and math.abs(a.y-b.y)<1e-10 end
function S.Get(edge)
    local d=A.StructureData
    if not d or d.version~=1 or not A.CrossingData or d.build~=A.CrossingData.build then return end
    local row=d.corridors and d.corridors[edge.structure]
    if not row or row.source~='native-wmo-floor' or row.samples<3 or row.maximumStep>.3 or row.headroom<2 then return end
    if not (same(edge.a,row.a) and same(edge.b,row.b) or same(edge.a,row.b) and same(edge.b,row.a)) then return end
    if not A.Terrain.Segment(row.a,row.a) or not A.Terrain.Segment(row.b,row.b) then return end
    return row
end
function S.Contains(p,id)
    local d=A.StructureData;local row=d and d.corridors[id]
    if not row or not A.TravelNetwork then return false end
    local x,y,instance=A.TravelNetwork.World(p)
    if not x then return false end
    local playerZ
    if UnitPosition then
        local ok,north,east,z=pcall(UnitPosition,'player')
        local function readable(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
        if ok and readable(north) and readable(east) and readable(z) and z~=0 and (east-x)^2+(north-y)^2<64 then
            playerZ=z
        end
    end
    local path=row.worldPath or {row.worldA,row.worldB}
    for i=2,#path do
        local a,b=path[i-1],path[i];local dx,dy=b[1]-a[1],b[2]-a[2];local length=dx*dx+dy*dy
        if length>1e-10 then
            local t=math.max(0,math.min(1,((x-a[1])*dx+(y-a[2])*dy)/length))
            if ((x-a[1])-t*dx)^2+((y-a[2])-t*dy)^2<=6.25 then
                local height=a[3]+(b[3]-a[3])*t
                if not row.worldPath and row.heightProfile then
                    for k=2,#row.heightProfile do if t<=row.heightProfile[k][1] then
                        local first,last=row.heightProfile[k-1],row.heightProfile[k]
                        local fraction=math.max(0,math.min(1,(t-first[1])/math.max(.000001,last[1]-first[1])))
                        height=first[2]+(last[2]-first[2])*fraction;break
                    end end
                end
                if not playerZ or math.abs(playerZ-height)<=1.5 then return true end
            end
        end
    end
    return false
end
function S.Path(id,from)
    local row=A.StructureData.corridors[id];local raw=row.worldPath or {row.worldA,row.worldB};local result={}
    local reverse=not same(from,row.a);local instance=A.CrossingData.maps[from.mapID].instance
    for i=1,#raw do
        local p=raw[reverse and #raw-i+1 or i]
        result[i]={worldX=p[1],worldY=p[2],instance=instance,structure=id}
    end
    return result
end
function S.Aim(world,map)
    local m=A.CrossingData.maps[map];if not m or world.instance~=m.instance then return end
    return {mapID=map,x=(m.west-world.worldX)/m.width,y=(m.north-world.worldY)/m.height}
end
