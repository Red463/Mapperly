local _,A=...
local S={};A.Structures=S
local function same(a,b) return a and b and a.mapID==b.mapID and math.abs(a.x-b.x)<1e-10 and math.abs(a.y-b.y)<1e-10 end
function S.Get(edge)
    local d=A.StructureData
    if not d or d.version~=1 or not A.CrossingData or d.build~=A.CrossingData.build then return end
    local row=d.corridors and d.corridors[edge.structure]
    if not row or (row.source~='native-wmo-floor' and row.source~='native-model-floor') or row.samples<3 or row.headroom<2 then return end
    local farholdeKerbs=row.placement==67711058 and row.wmo==7543871 and row.kerbSteps==2
    if row.maximumStep>(farholdeKerbs and .45 or .3) then return end
    if not (same(edge.a,row.a) and same(edge.b,row.b) or same(edge.a,row.b) and same(edge.b,row.a)) then return end
    if not A.Terrain.Segment(row.a,row.a) or not A.Terrain.Segment(row.b,row.b) then return end
    return row
end
function S.Contains(p,id,requireHeight)
    -- Remote pins describe a desired deck position. A new live start must
    -- supply readable nonzero elevation; zero is also this client's unknown
    -- placeholder. Existing routes may retain their approximate XY guidance.
    local d=A.StructureData;local row=d and d.corridors[id]
    if not row or not A.TravelNetwork then return false end
    local x,y,instance=A.TravelNetwork.World(p)
    local map=A.CrossingData and A.CrossingData.maps[row.a.mapID]
    if not x or not map or instance~=map.instance then return false end
    local playerZ
    if requireHeight~=false and UnitPosition then
        local ok,north,east,z=pcall(UnitPosition,'player')
        local function readable(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
        if ok and readable(north) and readable(east) and readable(z) and z~=0 and (east-x)^2+(north-y)^2<64 then
            playerZ=z
        end
    end
    if requireHeight and not playerZ then return false end
    local path=row.worldPath or {row.worldA,row.worldB}
    for i=2,#path do
        local a,b=path[i-1],path[i];local dx,dy=b[1]-a[1],b[2]-a[2];local length=dx*dx+dy*dy
        if length>1e-10 then
            local t=((x-a[1])*dx+(y-a[2])*dy)/length
            if t>=-1e-8 and t<=1+1e-8 and ((x-a[1])-t*dx)^2+((y-a[2])-t*dy)^2<=(row.radius or 2.5)^2 then
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
-- Only corridors with a separately sampled width proof can accept a route
-- endpoint on the deck. This never grants permission to the root terrain.
function S.Access(p,requireHeight)
    local d=A.StructureData;local network=A.TravelNetwork
    if not d or not network then return end
    for id,row in pairs(d.corridors) do
        if row.endpointAccess and S.Get({structure=id,a=row.a,b=row.b}) and S.Contains(p,id,requireHeight) then
            local path=S.Path(id,row.a);local x,y,instance=network.World(p)
            local best,index,projection,offset
            for i=2,#path do
                local a,b=path[i-1],path[i];local dx,dy=b.worldX-a.worldX,b.worldY-a.worldY
                local length=dx*dx+dy*dy
                local t=length>0 and ((x-a.worldX)*dx+(y-a.worldY)*dy)/length or 0
                local px,py=a.worldX+t*dx,a.worldY+t*dy;local distance=(x-px)^2+(y-py)^2
                if t>=-1e-8 and t<=1+1e-8 and (not best or distance<best) then best=distance;index=i;offset=i-1+t;projection={worldX=px,worldY=py,instance=instance,structure=id} end
            end
            local result={structure=id,offset=offset}
            for direction=1,2 do
                local points={{worldX=x,worldY=y,instance=instance,structure=id},projection}
                if direction==1 then for i=index-1,1,-1 do points[#points+1]=path[i] end
                else for i=index,#path do points[#points+1]=path[i] end end
                local length=0;for i=2,#points do length=length+network.Distance(points[i-1],points[i]) end
                result[#result+1]={structure=id,landing=direction==1 and row.a or row.b,path=points,distance=length}
            end
            return result
        end
    end
end
function S.Between(first,last)
    if not first or not last or first.structure~=last.structure then return end
    local id=first.structure;local row=A.StructureData.corridors[id]
    local full=S.Path(id,row.a)
    local path={first[1].path[1],first[1].path[2]}
    local forward=first.offset<=last.offset
    for k=1,#full do
        local i=forward and k or #full-k+1
        if forward and i>first.offset and i<last.offset or not forward and i<first.offset and i>last.offset then path[#path+1]=full[i] end
    end
    path[#path+1]=last[1].path[2];path[#path+1]=last[1].path[1]
    local length=0;for i=2,#path do length=length+A.TravelNetwork.Distance(path[i-1],path[i]) end
    return path,length,id
end
