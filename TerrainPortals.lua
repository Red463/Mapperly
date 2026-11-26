local _, A = ...
local P = {}
A.TerrainPortals = P

local floor, min, sqrt = math.floor, math.min, math.sqrt
local alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local decode = {}
for i=1,#alphabet do decode[alphabet:byte(i)] = i-1 end

-- Components are numbered in row-major order within each small tile, using
-- the same four-way connectivity as the compiler. A legal diagonal cannot
-- connect two components because both orthogonal neighbours must be open.
local function componentAt(z, cell, x, y, size)
    local left, top = floor(x/size)*size, floor(y/size)*size
    local w, h = min(size,z.w-left), min(size,z.h-top)
    local target = (y-top)*w+x-left
    local seen, component = {}, 0
    for seed=0,w*h-1 do
        if not seen[seed] and cell(z,left+seed%w,top+floor(seed/w)) then
            component = component+1
            local queue, head = {seed}, 1
            seen[seed] = true
            local function visit(id)
                if not seen[id] and cell(z,left+id%w,top+floor(id/w)) then
                    seen[id] = true
                    queue[#queue+1] = id
                end
            end
            while head<=#queue do
                local id=queue[head]; head=head+1
                if id==target then return component end
                local col,row=id%w,floor(id/w)
                if col>0 then visit(id-1) end
                if col+1<w then visit(id+1) end
                if row>0 then visit(id-w) end
                if row+1<h then visit(id+w) end
            end
        end
    end
end

-- Rows have variable-length records. Keep offsets only for rows visited by
-- this search, without unpacking an entire zone into tables at addon load.
local function reader(rows,width)
    local indexed={}
    return function(tile)
        local y,x=floor(tile/width),tile%width
        local row=rows[y+1]
        if not row then return end
        local offsets=indexed[y]
        if not offsets then
            offsets={};local pos=1
            for col=0,width-1 do
                local header=decode[row:byte(pos)]
                if not header then return end
                offsets[col]=pos
                pos=pos+1+4*(header%32)
            end
            if pos~=#row+1 then return end
            indexed[y]=offsets
        end
        local pos=offsets[x]
        return row,pos,decode[row:byte(pos)]
    end
end

-- Each span describes exactly one tile component. Fine-grid refinement
-- chooses the walk between the entry and exit cells. Never draw the coarse
-- graph itself or treat it as floor geometry.
function P.Trace(z,map,sx,sy,ex,ey,factor,cell,push,pop,charge)
    local data=A.WalkingPortalData
    local zone=data and data.version==1 and data.zones[map]
    if not zone or data.stride~=12 or zone.w~=z.w or zone.h~=z.h or zone.maskSha256~=z.maskSha256 then return end
    local size=data.stride
    local width,height=math.ceil(z.w/size),math.ceil(z.h/size)
    local rows=z.noSwimming and zone.dryRows or zone.rows
    if type(rows)~='table' or #rows~=height then return end
    local function tile(x,y) return floor(y/size)*width+floor(x/size) end
    local startTile,endTile=tile(sx,sy),tile(ex,ey)
    local first,last=componentAt(z,cell,sx,sy,size),componentAt(z,cell,ex,ey,size)
    if not first or not last then return end
    local source,goal=startTile*144+first,endTile*144+last
    local wx,wy=z.widthYards/z.w,z.heightYards/z.h
    local function distance(dx,dy) return sqrt((dx*wx)^2+(dy*wy)^2) end
    local read=reader(rows,width)
    local roads=factor>1 and A.Roads.Zone(map,z)
    local samples={}
    local function roadCost(x,y)
        local id=y*z.w+x
        if samples[id]==nil then samples[id]=A.Roads.Cell(roads,x,y) and 1 or factor end
        return samples[id]
    end
    local heap,states,closed={},{},{}
    states[source]={x=sx,y=sy,tile=startTile,component=first,g=0}
    push(heap,source,0,0)
    while #heap>0 do
        local entry=pop(heap);local id=entry.id
        local current=states[id]
        if not closed[id] and entry.g==current.g then
            if id==goal then
                local spans={}
                local tx,ty=ex,ey
                while current do
                    spans[#spans+1]={tile=current.tile,x=current.x,y=current.y,tx=tx,ty=ty}
                    if #spans%128==0 and A.Terrain.Checkpoint then A.Terrain.Checkpoint() end
                    tx,ty=current.leaveX,current.leaveY
                    current=current.parent
                end
                return spans,width
            end
            if not charge() then return end
            closed[id]=true
            local here=current.tile
            local _,_,header=read(here)
            if not header then return end
            local entranceCost=roads and header>=32 and roadCost(current.x,current.y) or factor
            local function edges(owner,reverse,axis)
                local row,pos,count=read(owner)
                if not row then return end
                local left,top=(owner%width)*size,floor(owner/width)*size
                for i=1,count%32 do
                    local at=pos+1+(i-1)*4
                    local n=0
                    for j=at,at+3 do n=n*64+(decode[row:byte(j)] or 0) end
                    local direction,offset=floor(n/262144),floor(n/16384)%16
                    local a,b=floor(n/128)%128,n%128
                    if (not reverse or axis==direction) and (reverse and b or a)==current.component then
                        local dst=owner+(direction==0 and 1 or width)
                        local key=reverse and owner*144+a or dst*144+b
                        if not closed[key] then
                            local x=left+(direction==0 and size-1 or offset)
                            local y=top+(direction==0 and offset or size-1)
                            local nx,ny=x+(direction==0 and 1 or 0),y+(direction==0 and 0 or 1)
                            if reverse then x,y,nx,ny=nx,ny,x,y end
                            local exitCost=roads and header>=32 and roadCost(x,y) or factor
                            local weight=(entranceCost+exitCost)/2
                            local g=current.g+weight*(distance(current.x-x,current.y-y)+(direction==0 and wx or wy))
                            if not states[key] or g<states[key].g then
                                states[key]={tile=reverse and owner or dst,component=reverse and a or b,x=nx,y=ny,
                                    parent=current,leaveX=x,leaveY=y,g=g}
                                push(heap,key,g+distance(ex-nx,ey-ny),g)
                            end
                        end
                    end
                end
            end
            edges(here,false)
            if here%width>0 then edges(here-1,true,0) end
            if here>=width then edges(here-width,true,1) end
        end
    end
    -- Exhausting the graph proves disconnection only for the exact masks
    -- used to compile it. A budget exit or newer correction still gets a
    -- normal detailed search. Road preference cannot join ground regions.
    local expected=z.noSwimming and zone.drySignature or zone.signature
    if expected and A.PathReuse and A.PathReuse.Signature(map,{
        preferRoads=false, allowSwimming=not z.noSwimming
    })==expected then
        return nil,'disconnected'
    end
end
