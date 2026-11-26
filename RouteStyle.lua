local _,A=...
local S={};A.RouteStyle=S
local teal={.075,.56,.60,1}
local minimapTeal={.29,.79,.81,1}
local ink={.035,.14,.16,.94}
local slate={.49,.57,.63,.48}
local fadedInk={.10,.14,.16,.38}
local shapes={chevron=true,triangle=true,none=true}

function S.Color(key,mini)
    local custom=A.db and A.db[key]
    if type(custom)=='table' then
        local valid=true
        for i=1,3 do
            local n=custom[i]
            if type(n)~='number' or not (n>=0 and n<=1) then valid=false;break end
        end
        if valid then return {custom[1],custom[2],custom[3],key=='routeCompletedColor' and slate[4] or 1} end
    end
    if key=='routeCompletedColor' then return slate end
    return mini and minimapTeal or teal
end

function S.Width()
    local width=A.db and A.db.routeLineWidth
    return type(width)=='number' and width>=1 and width<=6 and math.floor(width) or 3
end

function S.Shape()
    local shape=A.db and A.db.routeMarkerShape
    return shapes[shape] and shape or 'chevron'
end

function S.Completed(plan,i)
    local current=A.RouteProgress.Segment(plan)
    return current~=nil and i<current
end
function S.Kind(plan,i)
    if S.Completed(plan,i) then return 'completed' end
    if plan.points[i].transport or plan.points[i+1].transport then return 'transport' end
    return 'ahead'
end
function S.Key(plan)
    local J=A.Journey
    if not J or J.active~=plan then return tostring(plan)..':preview' end
    return tostring(plan)..':'..tostring(J and J.index)..':'..tostring(J and J.legIndex)..':'..tostring(J and J.structureIndex)..':'..tostring(J and J.crossing)
end
function S.Chevron(x,y,dx,dy,size)
    return x-dx*size-dy*size*.6,y-dy*size+dx*size*.6,x-dx*size+dy*size*.6,y-dy*size-dx*size*.6
end
function S.Hide(pool)
    for _,pair in ipairs(pool) do
        for _,line in ipairs(pair) do line:Hide() end
        for _,line in ipairs(pair.outline) do line:Hide() end
    end
end
function S.HideLines(pool)
    -- World-map lines are indexed by route point and may have gaps.
    for key,line in pairs(pool) do
        if key=='dots' then
            for _,dot in ipairs(line) do dot:Hide() end
        elseif key=='joins' then
            for _,join in ipairs(line) do join.edge:Hide();join.face:Hide() end
        else
            line:Hide()
            if line.routeCasing then line.routeCasing:Hide() end
        end
    end
end

local function showChevron(pool,index,parent,options,x,y,a,b,c,d)
    local thickness,anchor=options.thickness or 2,options.anchor
    local pair=pool[index]
    if not pair then
        pair={parent:CreateLine(nil,'OVERLAY'),parent:CreateLine(nil,'OVERLAY')}
        pair.outline={parent:CreateLine(nil,'OVERLAY'),parent:CreateLine(nil,'OVERLAY')}
        pool[index]=pair
        for k,face in ipairs(pair) do
            face:SetDrawLayer('OVERLAY',3);face:SetColorTexture(1,.96,.81,1)
            pair.outline[k]:SetDrawLayer('OVERLAY',2);pair.outline[k]:SetColorTexture(.03,.09,.10,.98)
        end
    end
    local triangle=options.shape=='triangle'
    if triangle and not pair[3] then
        pair[3]=parent:CreateLine(nil,'OVERLAY');pair[3]:SetDrawLayer('OVERLAY',3);pair[3]:SetColorTexture(1,.96,.81,1)
        pair.outline[3]=parent:CreateLine(nil,'OVERLAY');pair.outline[3]:SetDrawLayer('OVERLAY',2);pair.outline[3]:SetColorTexture(.03,.09,.10,.98)
    end
    for k=1,triangle and 3 or 2 do
        local face=pair[k]
        local edge=pair.outline[k]
        local ex,ey=k==1 and a or c,k==1 and b or d
        edge:SetThickness(thickness+1.5*(options.worldUnit or 1));face:SetThickness(thickness)
        local sx,sy=k==3 and a or x,k==3 and b or y
        edge:SetStartPoint(anchor,parent,sx,sy);face:SetStartPoint(anchor,parent,sx,sy)
        edge:SetEndPoint(anchor,parent,ex,ey);face:SetEndPoint(anchor,parent,ex,ey)
        edge:Show();face:Show()
    end
end

function S.Mark(pool,parent,ax,ay,bx,by,carry,used,options,consider)
    local dx,dy=bx-ax,by-ay;local length=math.sqrt(dx*dx+dy*dy)
    local gaps={}
    if length<.01 then return carry,used,gaps end
    dx,dy=dx/length,dy/length
    local distance=options.spacing-carry
    while distance<=length and used<options.limit do
        local x,y=ax+dx*distance,ay+dy*distance
        local a,b,c,d=S.Chevron(x,y,dx,dy,options.size)
        if not options.inside or options.inside(x,y) and options.inside(a,b) and options.inside(c,d) then
            if consider then
                consider(distance,x,y,a,b,c,d)
            else
                used=used+1
                showChevron(pool,used,parent,options,x,y,a,b,c,d)
                if not options.worldUnit then gaps[#gaps+1]={distance-options.size-2,distance+2} end
            end
        end
        distance=distance+options.spacing
    end
    return (carry+length)%options.spacing,used,gaps
end
function S.Pieces(ax,ay,bx,by,gaps)
    local dx,dy=bx-ax,by-ay;local length=math.sqrt(dx*dx+dy*dy)
    if length<.01 then return {} end
    local pieces={};local cursor=0
    local function append(first,last)
        if last-first>.01 then pieces[#pieces+1]={ax+dx*first/length,ay+dy*first/length,ax+dx*last/length,ay+dy*last/length} end
    end
    for _,gap in ipairs(gaps or {}) do append(cursor,math.max(cursor,math.min(length,gap[1])));cursor=math.max(cursor,math.min(length,gap[2])) end
    append(cursor,length);return pieces
end
local function reserveGap(segments,i,first,last)
    local s=segments[i]
    s.gaps[#s.gaps+1]={math.max(0,first),math.min(s.length,last)}
    -- Keep space around the glyph across dense route vertices, but never
    -- continue a gap across a teleport, clipped break or change of style.
    local j=i
    while first<0 and segments[j].connected do
        j=j-1;local p=segments[j]
        first=first+p.length;p.gaps[#p.gaps+1]={math.max(0,first),p.length}
    end
    last=last-s.length;j=i+1
    while last>0 and segments[j] and segments[j].connected do
        local p=segments[j];p.gaps[#p.gaps+1]={0,math.min(last,p.length)}
        last=last-p.length;j=j+1
    end
end

local function markRoute(segments,markers,parent,options)
    local carry,used=0,0
    local best,index,position,glyph,fromPlayer,foundForward
    local function consider(distance,x,y,a,b,c,d)
        local radius2=x*x+y*y
        -- On switchbacks, a later returning leg may pass closer to the player.
        -- Prefer the first cue along their current, unbroken walking stretch.
        if not foundForward and (fromPlayer or not best or radius2<best) then
            best=radius2;position=distance;glyph={x,y,a,b,c,d,index}
            foundForward=fromPlayer
        end
    end
    for i,s in ipairs(segments) do
        if not s.connected then carry=0;fromPlayer=false end
        if s.fromPlayer then fromPlayer=true end
        if s.kind=='ahead' then
            index=i
            local gaps
            carry,used,gaps=S.Mark(markers,parent,s[1],s[2],s[3],s[4],carry,used,options,options.minimap and consider)
            for _,g in ipairs(gaps) do reserveGap(segments,i,g[1],g[2]) end
            if foundForward or used>=options.limit then break end
        end
    end
    if glyph then
        showChevron(markers,1,parent,options,unpack(glyph,1,6))
        reserveGap(segments,glyph[7],position-options.size-2,position+2)
    end
end

local function subpixel(region)
    if region.SetSnapToPixelGrid then region:SetSnapToPixelGrid(false) end
    if region.SetTexelSnappingBias then region:SetTexelSnappingBias(0) end
end

local function paintStroke(line,parent,anchor,ax,ay,bx,by,color,edgeColor,width,border,world)
    local edge=line.routeCasing
    if not edge then
        edge=parent:CreateLine(nil,'OVERLAY');line.routeCasing=edge
        edge:SetDrawLayer('OVERLAY',-1);line:SetDrawLayer('OVERLAY',0)
        if world then subpixel(line);subpixel(edge) end
    end
    edge:SetThickness(width+border);edge:SetColorTexture(unpack(edgeColor))
    line:SetThickness(width);line:SetColorTexture(unpack(color))
    edge:SetStartPoint(anchor,parent,ax,ay);line:SetStartPoint(anchor,parent,ax,ay)
    edge:SetEndPoint(anchor,parent,bx,by);line:SetEndPoint(anchor,parent,bx,by)
    edge:Show();line:Show()
end

local function stroke(base,pool,parent,ax,ay,bx,by,gaps,used,anchor,color,edgeColor,width)
    local pieces=S.Pieces(ax,ay,bx,by,gaps)
    base:Hide()
    if base.routeCasing then base.routeCasing:Hide() end
    for i,piece in ipairs(pieces) do
        local line=base
        if i>1 then used=used+1;line=pool[used];if not line then line=parent:CreateLine(nil,'OVERLAY');pool[used]=line end end
        paintStroke(line,parent,anchor,piece[1],piece[2],piece[3],piece[4],color,edgeColor,width,1.5)
    end
    return used
end

-- Native lines have flat ends. A matching round join fills the open wedge
-- on the outside of a bend. Both fills draw above every piece of casing.
local function joinAt(pool,index,parent,anchor,x,y,color,edgeColor,width,border)
    local join=pool[index]
    if not join then
        join={edge=parent:CreateTexture(nil,'OVERLAY',nil,-1),face=parent:CreateTexture(nil,'OVERLAY',nil,0)}
        for _,tex in pairs(join) do
            tex:SetTexture('Interface\\AddOns\\Mapperly\\Media\\RouteJoin')
            subpixel(tex)
        end
        pool[index]=join
    end
    local edge,face=join.edge,join.face
    edge:ClearAllPoints();face:ClearAllPoints()
    edge:SetPoint('CENTER',parent,anchor,x,y);face:SetPoint('CENTER',parent,anchor,x,y)
    edge:SetSize(width+border,width+border);face:SetSize(width,width)
    edge:SetVertexColor(unpack(edgeColor));face:SetVertexColor(unpack(color))
    edge:Show();face:Show()
end

local function dotAt(pool,index,parent,anchor,x,y,size)
    local dot=pool[index]
    if not dot then
        dot=parent:CreateTexture(nil,'OVERLAY',nil,1)
        dot:SetTexture('Interface\\AddOns\\Mapperly\\Media\\RouteDot')
        pool[index]=dot
    end
    dot:ClearAllPoints();dot:SetPoint('CENTER',parent,anchor,x,y)
    dot:SetSize(size,size);dot:Show()
end

function S.Render(segments,markers,fragments,parent,options)
    options.shape=S.Shape()
    local widthFactor=S.Width()/3
    local strokeWidth=options.strokeWidth*widthFactor
    local aheadColor=S.Color('routeAheadColor',options.minimap)
    local completedColor=S.Color('routeCompletedColor')
    local dotted,dashed=0,0
    for i,s in ipairs(segments) do
        local dx,dy=s[3]-s[1],s[4]-s[2]
        s.length=math.sqrt(dx*dx+dy*dy);s.gaps={}
        local p=segments[i-1]
        s.connected=p and not s.split and p.kind==s.kind and (p[3]-s[1])^2+(p[4]-s[2])^2<.0001
        if s.kind=='transport' then dotted=dotted+s.length
        elseif s.kind=='completed' then dashed=dashed+s.length end
    end
    if options.shape~='none' then markRoute(segments,markers,parent,options) end
    -- A long visible route gets wider spacing instead of allocating thousands
    -- of decorative regions or cutting off the last half of a sailing leg.
    local mini,unit=options.minimap,options.worldUnit
    local dotPeriod=math.max(mini and 9 or 12*(unit or 1),dotted/(mini and 48 or 320))
    local dashPeriod=math.max(mini and 9 or 13,dashed/(mini and 48 or 360))
    local phase,usedDots,usedFragments,usedJoins=0,0,0,0
    fragments.dots=fragments.dots or {}
    if unit then fragments.joins=fragments.joins or {} end
    for _,s in ipairs(segments) do
        if not s.connected then phase=0 end
        if s.kind=='transport' then
            s.base:Hide()
            if s.base.routeCasing then s.base.routeCasing:Hide() end
            -- Half-open segments let adjoining vertices share one regular
            -- pattern rather than stacking dots at each native sample.
            local at=(-phase)%dotPeriod
            while at<s.length-.0001 do
                local t=at/s.length
                local x,y=s[1]+(s[3]-s[1])*t,s[2]+(s[4]-s[2])*t
                if not options.inside or options.inside(x,y) then
                    usedDots=usedDots+1
                    dotAt(fragments.dots,usedDots,parent,options.anchor,x,y,(mini and 3.8 or 4.6*(unit or 1))*math.sqrt(widthFactor))
                end
                at=at+dotPeriod
            end
            phase=(phase+s.length)%dotPeriod
        elseif unit then
            local completed=s.kind=='completed'
            local color,edgeColor=completed and completedColor or aheadColor,completed and fadedInk or ink
            local width,border=strokeWidth-(completed and .65*unit*widthFactor or 0),1.5*unit
            paintStroke(s.base,parent,options.anchor,s[1],s[2],s[3],s[4],color,edgeColor,width,border,true)
            if s.connected then
                usedJoins=usedJoins+1
                joinAt(fragments.joins,usedJoins,parent,options.anchor,s[1],s[2],color,edgeColor,width,border)
            end
        else
            local completed=s.kind=='completed'
            if completed then
                local at=dashPeriod*.57-phase
                while at<s.length do
                    s.gaps[#s.gaps+1]={at,at+dashPeriod*.43};at=at+dashPeriod
                end
                phase=(phase+s.length)%dashPeriod
            elseif #s.gaps>1 then
                table.sort(s.gaps,function(a,b) return a[1]<b[1] end)
            end
            usedFragments=stroke(s.base,fragments,parent,s[1],s[2],s[3],s[4],s.gaps,
                usedFragments,options.anchor,completed and completedColor or aheadColor,
                completed and fadedInk or ink,strokeWidth-(completed and .65*widthFactor or 0))
        end
    end
end
