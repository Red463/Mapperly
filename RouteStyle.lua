local _,A=...
local S={};A.RouteStyle=S
function S.Completed(plan,i)
    local J=A.Journey
    if not J or J.active~=plan then return false end
    local through=(J.index or 1)-2
    local leg=J.Leg()
    if J.crossing and leg and leg.exitPath and leg.corridorStart then through=math.max(through,leg.corridorStart+(J.structureIndex or 2)-3) end
    return i<=through
end
function S.Color(plan,i,alpha)
    if S.Completed(plan,i) then return .48,.43,.34,.3 end
    if plan.points[i].transport or plan.points[i+1].transport then return .3,.75,1,alpha or .9 end
    return 1,.77,.18,alpha or .9
end
function S.Key(plan)
    local J=A.Journey
    if not J or J.active~=plan then return tostring(plan)..':preview' end
    return tostring(plan)..':'..tostring(J and J.index)..':'..tostring(J and J.legIndex)..':'..tostring(J and J.structureIndex)..':'..tostring(J and J.crossing)
end
function S.Chevron(x,y,dx,dy,size)
    return x-dx*size-dy*size*.6,y-dy*size+dx*size*.6,x-dx*size+dy*size*.6,y-dy*size-dx*size*.6
end
function S.Hide(pool) for _,pair in ipairs(pool) do pair[1]:Hide();pair[2]:Hide();for _,line in ipairs(pair.outline or {}) do line:Hide() end end end
function S.Mark(pool,parent,ax,ay,bx,by,carry,used,options)
    local dx,dy=bx-ax,by-ay;local length=math.sqrt(dx*dx+dy*dy)
    local gaps={}
    if length<.01 then return carry,used,gaps end
    dx,dy=dx/length,dy/length
    local distance=options.spacing-carry
    while distance<=length and used<options.limit do
        local x,y=ax+dx*distance,ay+dy*distance
        local a,b,c,d=S.Chevron(x,y,dx,dy,options.size)
        if not options.inside or options.inside(x,y) and options.inside(a,b) and options.inside(c,d) then
            used=used+1;local pair=pool[used]
            if not pair then
                local outline={parent:CreateLine(nil,'OVERLAY'),parent:CreateLine(nil,'OVERLAY')}
                pair={parent:CreateLine(nil,'OVERLAY'),parent:CreateLine(nil,'OVERLAY')};pair.outline=outline;pool[used]=pair
            end
            gaps[#gaps+1]={distance-options.size-3,distance+3}
            for k,line in ipairs(pair) do
                local shadow=pair.outline[k]
                -- Same-layer creation order is not a render-order guarantee.
                -- Keep outline, route and bright face on explicit sublevels.
                shadow:SetDrawLayer('OVERLAY',2)
                shadow:SetThickness((options.thickness or 2.5)+2);shadow:SetColorTexture(.045,.03,.015,1)
                shadow:SetStartPoint(options.anchor,parent,x,y);shadow:SetEndPoint(options.anchor,parent,k==1 and a or c,k==1 and b or d);shadow:Show()
                line:SetDrawLayer('OVERLAY',3)
                line:SetThickness(options.thickness or 2.5);line:SetColorTexture(1,.96,.78,.98)
                line:SetStartPoint(options.anchor,parent,x,y)
                line:SetEndPoint(options.anchor,parent,k==1 and a or c,k==1 and b or d);line:Show()
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
function S.Render(segments,markers,fragments,parent,options)
    for i,s in ipairs(segments) do
        local dx,dy=s[3]-s[1],s[4]-s[2];s.length=math.sqrt(dx*dx+dy*dy);s.gaps={}
        local p=segments[i-1]
        s.connected=p and not s.split and p.markable and s.markable and (p[3]-s[1])^2+(p[4]-s[2])^2<.0001
    end
    local carry,used=0,0
    for i,s in ipairs(segments) do
        if not s.connected then carry=0 end
        if s.markable then
            local gaps;carry,used,gaps=S.Mark(markers,parent,s[1],s[2],s[3],s[4],carry,used,options)
            for _,g in ipairs(gaps) do
                s.gaps[#s.gaps+1]={math.max(0,g[1]),math.min(s.length,g[2])}
                -- Reserve the entire marker footprint across dense bends too.
                -- Never propagate a visual gap across a teleport or player gap.
                local first,j=g[1],i
                while first<0 and segments[j].connected do
                    j=j-1;local p=segments[j];p.gaps[#p.gaps+1]={math.max(0,p.length+first),p.length};first=first+p.length
                end
                local last=g[2]-s.length;j=i+1
                while last>0 and segments[j] and segments[j].connected do
                    local p=segments[j];p.gaps[#p.gaps+1]={0,math.min(last,p.length)};last=last-p.length;j=j+1
                end
            end
        else carry=0 end
    end
    local usedFragments=0
    for _,s in ipairs(segments) do
        table.sort(s.gaps,function(a,b) return a[1]<b[1] end)
        usedFragments=S.Stroke(s.base,fragments,parent,s[1],s[2],s[3],s[4],s.gaps,usedFragments,options.anchor,s.color,options.strokeWidth)
    end
end
function S.Stroke(base,pool,parent,ax,ay,bx,by,gaps,used,anchor,color,thickness)
    local pieces=S.Pieces(ax,ay,bx,by,gaps)
    base:Hide()
    for i,piece in ipairs(pieces) do
        local line=base
        if i>1 then used=used+1;line=pool[used];if not line then line=parent:CreateLine(nil,'OVERLAY');pool[used]=line end end
        line:SetThickness(thickness);line:SetColorTexture(unpack(color))
        line:SetStartPoint(anchor,parent,piece[1],piece[2]);line:SetEndPoint(anchor,parent,piece[3],piece[4]);line:Show()
    end
    return used
end
