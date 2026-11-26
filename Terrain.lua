local _, A = ...
local T={}; A.Terrain=T
local floor,abs,sqrt,min,max=math.floor,math.abs,math.sqrt,math.min,math.max
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local decode={};for i=1,#alphabet do decode[alphabet:byte(i)]=i-1 end
local powers={32,16,8,4,2,1}
local expanded={}
for byte=0,255 do
 local bits=decode[byte];local chunk={}
 for i=1,6 do chunk[i]=string.char(bits and floor(bits/powers[i])%2 or 0) end
 expanded[string.char(byte)]=table.concat(chunk)
end
local function number(n)
 return not (issecretvalue and issecretvalue(n)) and type(n)=='number' and n==n and n>-math.huge and n<math.huge
end
local function position(p)
 return type(p)=='table' and number(p.mapID) and p.mapID>0 and p.mapID%1==0 and number(p.x) and number(p.y) and p.x>=0 and p.x<=1 and p.y>=0 and p.y<=1
end
local function point(p) return {mapID=p.mapID,x=p.x,y=p.y} end
local function copy(v,seen)
 if type(v)~='table' then return v end
 seen=seen or {};if seen[v] then return seen[v] end
 local r={};seen[v]=r;for k,value in pairs(v) do r[k]=copy(value,seen) end;return r
end
function T.Zone(mapID)
 if not number(mapID) or mapID<1 or mapID%1~=0 then return nil,'unavailable' end
 local data=A.TerrainData
 local z=type(data)=='table' and data.version==1 and type(data.zones)=='table' and data.zones[mapID]
 if type(z)~='table' or (z.status~='complete' and z.status~='partial') or not number(z.w) or not number(z.h) or z.w<1 or z.h<1 or z.w%1~=0 or z.h%1~=0 or z.w>8192 or z.h>8192 or not number(z.widthYards) or not number(z.heightYards) or z.widthYards<=0 or z.heightYards<=0 or type(z.rows)~='table' then return nil,'unavailable' end
 local patches=A.GroundCorrectionData
 local patch=patches and patches.version==1 and patches.zones[mapID]
 z.groundRows=patch and patch.baseSha256==z.maskSha256 and patch.w==z.w and patch.h==z.h and patch.rows or nil
 return z
end
local decodedZone,decodedWidth,decodedRows,decodedOrder,decodedBytes=nil,nil,{},{},0
local policyViews=setmetatable({},{__mode='k'})
-- Keep the public base zone unchanged: region labels and certified native
-- floors describe the source mask. Search views add the requested liquid policy.
function T.PolicyZone(mapID,options)
 local z,reason=T.Zone(mapID);if not z then return nil,reason end
 local allowed=A.Water and A.Water.AllowSwimming(options)
 if not A.Water then allowed=not (type(options)=='table' and options.allowSwimming==false or A.db and A.db.allowSwimming==false) end
 if allowed then return z end
 local water=A.Water and A.Water.Zone(mapID,z)
 local view=policyViews[z]
 if not view or view.water~=water then view=setmetatable({noSwimming=true,water=water},{__index=z});policyViews[z]=view end
 return view
end
local function cell(z,x,y)
 if x<0 or y<0 or x>=z.w or y>=z.h then return false end
 if z.noSwimming and (not A.Water or not A.Water.Cell(z.water,x,y)) then return false end
 local row=z.rows[y+1];if type(row)~='string' then return false end
 if decodedZone~=z or decodedWidth~=z.w then
  decodedZone=z;decodedWidth=z.w;decodedRows={};decodedOrder={};decodedBytes=0
 end
 local decoded=decodedRows[row]
 if not decoded then
  -- Expand a packed row in C once, rather than decoding its bits on every
  -- search neighbor. Unknown bytes stay prohibited; absent cells stay absent.
  decoded=row:sub(1,math.ceil(z.w/6)):gsub('.',expanded):sub(1,z.w)
  while #decodedOrder>=8192 or decodedBytes+#decoded>4194304 do
   local old=table.remove(decodedOrder,1);decodedBytes=decodedBytes-#decodedRows[old];decodedRows[old]=nil
  end
  decodedRows[row]=decoded;decodedOrder[#decodedOrder+1]=row;decodedBytes=decodedBytes+#decoded
 end
 if decoded:byte(x+1)==1 then return true end
 local extra=z.groundRows and z.groundRows[y+1]
 local bits=type(extra)=='string' and decode[extra:byte(floor(x/6)+1)]
 return bits and floor(bits/powers[x%6+1])%2==1 or false
end
local function coordinates(z,p) return min(z.w-1,floor(p.x*z.w)),min(z.h-1,floor(p.y*z.h)) end
function T.Allowed(p,options)
 if not position(p) then return false end
 local z=T.PolicyZone(p.mapID,options);if not z then return false end
 local x,y=coordinates(z,p);return cell(z,x,y)
end
local function touches(z,x,y)
 local ix,iy=min(z.w-1,floor(x)),min(z.h-1,floor(y))
 if not cell(z,ix,iy) then return false end
 local left=x>0 and x<z.w and abs(x-floor(x+.5))<1e-10
 local up=y>0 and y<z.h and abs(y-floor(y+.5))<1e-10
 if left and not cell(z,ix-1,iy) then return false end
 if up and not cell(z,ix,iy-1) then return false end
 if left and up and not cell(z,ix-1,iy-1) then return false end
 return true
end
-- Grid traversal visits every touched cell, including both sides of a corner
-- or grid edge. A diagonal may never slip between two prohibited cells.
local function segment(z,a,b)
 local ax,ay,bx,by=a.x*z.w,a.y*z.h,b.x*z.w,b.y*z.h
 if not touches(z,ax,ay) or not touches(z,bx,by) then return false end
 local x,y=coordinates(z,a);local ex,ey=coordinates(z,b)
 local dx,dy=bx-ax,by-ay
 if dx==0 and dy==0 then return true end
 local sx=dx>0 and 1 or dx<0 and -1 or 0;local sy=dy>0 and 1 or dy<0 and -1 or 0
 local tx=dx==0 and math.huge or ((sx>0 and x+1 or x)-ax)/dx
 local ty=dy==0 and math.huge or ((sy>0 and y+1 or y)-ay)/dy
 local dtx=dx==0 and math.huge or abs(1/dx);local dty=dy==0 and math.huge or abs(1/dy)
 local vertical=dx==0 and ax>0 and ax<z.w and abs(ax-floor(ax+.5))<1e-10
 local horizontal=dy==0 and ay>0 and ay<z.h and abs(ay-floor(ay+.5))<1e-10
 local work=0
 while true do
  if not cell(z,x,y) or (vertical and not cell(z,x-1,y)) or (horizontal and not cell(z,x,y-1)) then return false end
  if x==ex and y==ey then return true end
  -- The endpoint's touching cells were checked above. Do not step beyond it
  -- when a negative-going axis lands exactly on a grid boundary.
  if min(tx,ty)>=1-1e-12 then return true end
  work=work+1;if work%256==0 and T.Checkpoint then T.Checkpoint() end
  if abs(tx-ty)<1e-10 then
   if not cell(z,x+sx,y) or not cell(z,x,y+sy) then return false end
   x=x+sx;y=y+sy;tx=tx+dtx;ty=ty+dty
  elseif tx<ty then x=x+sx;tx=tx+dtx
  else y=y+sy;ty=ty+dty end
 end
end
function T.Segment(a,b,options)
 if not position(a) or not position(b) or a.mapID~=b.mapID then return false end
 local z=T.PolicyZone(a.mapID,options);return z and segment(z,a,b) or false
end
local function yards(z,a,b) return sqrt(((a.x-b.x)*z.widthYards)^2+((a.y-b.y)*z.heightYards)^2) end
function T.Approach(p,maxYards,options)
 if not position(p) then return nil,'invalid point' end
 local z,reason=T.PolicyZone(p.mapID,options);if not z then return nil,reason end
 if segment(z,p,p) then return point(p) end
 maxYards=maxYards==nil and 30 or maxYards
 if not number(maxYards) or maxYards<0 then return nil,'invalid distance' end
 local cx,cy=coordinates(z,p);local rx=min(z.w,math.ceil(maxYards*z.w/z.widthYards)+1);local ry=min(z.h,math.ceil(maxYards*z.h/z.heightYards)+1)
 local best,bestDistance;local work=0
 for y=max(0,cy-ry),min(z.h-1,cy+ry) do
  for x=max(0,cx-rx),min(z.w-1,cx+rx) do
   work=work+1;if work>16384 then return nil,'budget' end
   if cell(z,x,y) then
    local candidate={mapID=p.mapID,x=(x+.5)/z.w,y=(y+.5)/z.h};local d=yards(z,p,candidate)
    if d<=maxYards+1e-8 and (not bestDistance or d<bestDistance) then best=candidate;bestDistance=d end
   end
  end
 end
 if best then return best end
 return nil,'no approach'
end
local cachedZone,cachedRoads,cachedGround,cache,order,cachePoints=nil,nil,nil,{},{},0
local cachedRows,cachedShape={},{}
local cachedWaterRows={}
local cachedRoadFactor
-- PathReuse owns the cross-zone cache; invalidate this legacy inner cache
-- before a fresh search when its content fingerprint changes.
function T.ClearPathCache()
 cachedZone=nil;cache={};order={};cachePoints=0
end
local function refreshCache(z,roads,roadFactor)
 local changed=cachedZone~=z or cachedRoads~=roads or cachedRoadFactor~=roadFactor or cachedGround~=z.groundRows or cachedShape[1]~=z.w or cachedShape[2]~=z.h or cachedShape[3]~=z.widthYards or cachedShape[4]~=z.heightYards
 if not changed then
  for i=1,z.h do if cachedRows[i]~=z.rows[i] then changed=true;break end end
  if not changed then for i=1,z.h do if cachedWaterRows[i]~=(z.water and z.water.rows[i]) then changed=true;break end end end
 end
 if changed then
  cachedZone=z;cachedRoads=roads;cachedRoadFactor=roadFactor;cachedGround=z.groundRows;cache={};order={};cachePoints=0;cachedRows={};cachedShape={z.w,z.h,z.widthYards,z.heightYards}
  for i=1,z.h do cachedRows[i]=z.rows[i] end
  cachedWaterRows={};if z.water then for i=1,z.h do cachedWaterRows[i]=z.water.rows[i] end end
 end
end
local function cacheKey(a,b)
 local first=string.format('%.17g,%.17g',a.x,a.y);local last=string.format('%.17g,%.17g',b.x,b.y)
 if first>last then return a.mapID..':'..last..':'..first,true end
 return a.mapID..':'..first..':'..last,false
end
local function pathCopy(points,reverse)
 local result={};for i=1,#points do result[i]=point(points[reverse and #points-i+1 or i]) end;return result
end
local function remember(key,reverse,points,length,reason)
 if cache[key] then return end
 local count=points and #points or 0
 -- A 40-area graph has up to 780 pairs. Retain its useful results without
 -- retaining more geometry: impossible pairs use only a bounded small entry.
 while #order>=1024 or cachePoints+count>8192 do
  local oldest=table.remove(order,1);local entry=cache[oldest]
  cachePoints=cachePoints-(entry.points and #entry.points or 0);cache[oldest]=nil
 end
 order[#order+1]=key;cache[key]={points=points and pathCopy(points,reverse) or nil,length=length,reason=reason}
 cachePoints=cachePoints+count
end
-- The heap admits replacement entries; stale entries are discarded on pop.
local function push(heap,id,f,g)
 local i=#heap+1;local value={id=id,f=f,g=g}
 while i>1 do local parent=floor(i/2);if heap[parent].f<=f then break end;heap[i]=heap[parent];i=parent end
 heap[i]=value
end
local function pop(heap)
 local first,last=heap[1],table.remove(heap);if #heap==0 then return first end
 local i=1
 while i*2<=#heap do
  local child=i*2;if child<#heap and heap[child+1].f<heap[child].f then child=child+1 end
  if heap[child].f>=last.f then break end
  heap[i]=heap[child];i=child
 end
 heap[i]=last;return first
end
local neighbors={{-1,0},{1,0},{0,-1},{0,1},{-1,-1},{-1,1},{1,-1},{1,1}}
function T.Path(a,b,options)
 if not position(a) or not position(b) then return nil,'invalid point' end
 if a.mapID~=b.mapID then return nil,'map mismatch' end
 local z,reason=T.PolicyZone(a.mapID,options);if not z then return nil,reason end
 if A.PlanningJob then A.PlanningJob.BeginPath(a.mapID) end
 options=type(options)=='table' and options or {}
 local maxDistance=options.maxDistance
 if maxDistance~=nil and (not number(maxDistance) or maxDistance<0) then return nil,'invalid distance' end
 if not segment(z,a,a) or not segment(z,b,b) then return nil,'blocked endpoint' end
 local direct=yards(z,a,b)
 if maxDistance and direct>maxDistance+.000001 then return nil,'too long' end
 local roads=options.preferRoads and A.Roads and A.Roads.Zone(a.mapID,z)
 local roadFactor=roads and select(3,A.Roads.Strength(options.roadPreferenceStrength)) or 1
 -- A clear straight line may still be worse than a modest road detour.
 if not roads and segment(z,a,b) then return {point(a),point(b)},direct end
 refreshCache(z,roads,roadFactor)
 local key,reverse=cacheKey(a,b);local hit=cache[key]
 if hit then
  if not hit.points then return nil,hit.reason end
  if not maxDistance or hit.length<=maxDistance+.000001 then return pathCopy(hit.points,reverse),hit.length end
 end
 -- A failed local search says nothing about longer paths across this zone.
 -- Keep range-scoped failures separate from unrestricted cached results.
 local rangeKey=maxDistance and (key..'@'..string.format('%.17g',maxDistance))
 if rangeKey and cache[rangeKey] then return nil,cache[rangeKey].reason end
 local budget=options.maxExpansions or options.budget or 16384
 if not number(budget) or budget<0 then return nil,'invalid budget' end
 budget=min(262144,floor(budget))
 local yield=type(options.yield)=='function' and options.yield
 local sx,sy=coordinates(z,a);local ex,ey=coordinates(z,b);local start=sy*z.w+sx;local goal=ey*z.w+ex
 local wx,wy=z.widthYards/z.w,z.heightYards/z.h
 local diagonal=sqrt(wx*wx+wy*wy)
 local factors={}
 local function factor(x,y)
  if not roads then return 1 end
  if x<0 or y<0 or x>=z.w or y>=z.h then return roadFactor end
  local id=y*z.w+x;local value=factors[id]
  if not value then value=A.Roads.Cell(roads,x,y) and 1 or roadFactor;factors[id]=value end
  return value
 end
 local major2,minor2,ux,uy,mx,my
 if maxDistance then
  -- Every point on a path of length L lies inside the ellipse whose foci
  -- are its endpoints and whose distance sum is L. Pad for grid centres;
  -- do not search the rest of the zone for a local 450-yard connection.
  local allowance=maxDistance+2*diagonal
  major2=(allowance/2)^2;minor2=major2-(direct/2)^2
  ux=(b.x-a.x)*z.widthYards/direct;uy=(b.y-a.y)*z.heightYards/direct
  mx=(a.x+b.x)*z.widthYards/2;my=(a.y+b.y)*z.heightYards/2
 end
 local function inRange(x,y)
  local dx,dy=(x+.5)*wx-mx,(y+.5)*wy-my
  local along,across=dx*ux+dy*uy,dx*uy-dy*ux
  return along*along/major2+across*across/minor2<=1.000000001
 end
 -- Exact unobstructed eight-neighbor distance is admissible on rectangular
 -- cells and avoids exploring the extra area admitted by Euclidean distance.
 local function heuristic(x,y,tx,ty)
  local dx,dy=abs(tx-x),abs(ty-y);local common=min(dx,dy)
  return common*diagonal+(dx-common)*wx+(dy-common)*wy
 end
 local work,reported=0,0
 local function reportWork()
  if work<=reported then return end
  reported=work
  if A.PlanningJob then A.PlanningJob.PathProgress(work) end
  local checkpoint=yield or T.Checkpoint
  if checkpoint then checkpoint(work) end
 end
 local function finish(path,reason)
  reportWork();return path,reason
 end
 local function charge()
  if work>=budget then return false end
  work=work+1
  if work%256==0 then reportWork() end
  return true
 end
 -- Integrate cost over cell-boundary crossings so smoothing cannot erase
 -- road bends or accumulate sampling errors along long straight segments.
 -- The supercover predicate remains the authority for terrain safety.
 local function weighted(a,b)
  local ax,ay=a.x*z.w,a.y*z.h;local dx,dy=(b.x-a.x)*z.w,(b.y-a.y)*z.h
  local x,y=coordinates(z,a);local sx,sy=dx>0 and 1 or -1,dy>0 and 1 or -1
  local tx=dx==0 and math.huge or ((sx>0 and x+1 or x)-ax)/dx
  local ty=dy==0 and math.huge or ((sy>0 and y+1 or y)-ay)/dy
  local dtx=dx==0 and math.huge or abs(1/dx);local dty=dy==0 and math.huge or abs(1/dy)
  local at,sum,work=0,0,0
  while at<1 do
   local nextT=min(1,tx,ty)
   sum=sum+max(0,nextT-at)*factor(x,y);at=nextT
   if at>=1 then break end
   if abs(tx-ty)<1e-10 then x=x+sx;y=y+sy;tx=tx+dtx;ty=ty+dty
   elseif tx<ty then x=x+sx;tx=tx+dtx else y=y+sy;ty=ty+dty end
   work=work+1;if work%256==0 and T.Checkpoint then T.Checkpoint() end
  end
  return yards(z,a,b)*sum
 end
 local function search(tile,tileWidth,limit,from,to)
  local initial,target=from or start,to or goal
  local tx,ty=target%z.w,floor(target/z.w)
  local heap,scores,previous,closed={},{[initial]=0},{},{};push(heap,initial,0,0)
  while #heap>0 do
   local entry=pop(heap);local id=entry.id
   if not closed[id] and entry.g==scores[id] then
    if id==target then return previous end
    if work>=limit or not charge() then return end
    closed[id]=true
    local x,y=id%z.w,floor(id/z.w);local currentFactor=factor(x,y)
    for _,offset in ipairs(neighbors) do
     local dx,dy=offset[1],offset[2];local nx,ny=x+dx,y+dy;local nid=ny*z.w+nx
     if not closed[nid] and (not tile or floor(ny/12)*tileWidth+floor(nx/12)==tile) and cell(z,nx,ny) and (not maxDistance or inRange(nx,ny)) and (dx==0 or dy==0 or (cell(z,x+dx,y) and cell(z,x,y+dy))) then
      local g=entry.g+(dx==0 and wy or dy==0 and wx or diagonal)*(currentFactor+factor(nx,ny))/2
      if not scores[nid] or g<scores[nid] then scores[nid]=g;previous[nid]=id;push(heap,nid,g+heuristic(nx,ny,tx,ty),g) end
     end
    end
   end
  end
 end
 local previous,raw
 local function center(x,y) return {mapID=a.mapID,x=(x+.5)/z.w,y=(y+.5)/z.h} end
 local function refineSpans(spans,width,limit)
  local result={point(a)}
  for i=#spans,1,-1 do
   local span=spans[i]
   local first,last=center(span.x,span.y),center(span.tx,span.ty)
   if not segment(z,result[#result],first) then return end
   result[#result+1]=first
   if span.x~=span.tx or span.y~=span.ty then
    if not roads and segment(z,first,last) then
     result[#result+1]=last
    else
     local entry=span.y*z.w+span.x;local exit=span.ty*z.w+span.tx
     local back=search(span.tile,width,limit,entry,exit)
     if not back then return end
     local chain={};local id=exit
     while id~=entry do chain[#chain+1]=id;id=back[id] end
     for j=#chain,1,-1 do id=chain[j];result[#result+1]=center(id%z.w,floor(id/z.w)) end
    end
   end
   if i%12==0 and T.Checkpoint then T.Checkpoint() end
  end
  if not segment(z,result[#result],b) then return end
  result[#result+1]=point(b)
  return result
 end
 if not maxDistance and budget>=16384 and max(abs(ex-sx),abs(ey-sy))>=96 then
  if A.TerrainPortals then
   local function chargeGuide() return work<min(42000,budget*.85) and charge() end
   local spans,width=A.TerrainPortals.Trace(z,a.mapID,sx,sy,ex,ey,roadFactor,cell,push,pop,chargeGuide)
   if width=='disconnected' then return finish(nil,'unreachable') end
   if spans then raw=refineSpans(spans,width,budget) end
  end
 end
 if not raw and not previous then previous=search(nil,nil,budget) end
 if not raw and not previous then
  if work>=budget then return finish(nil,'budget') end
  local why=maxDistance and 'too long' or 'unreachable'
  remember(rangeKey or key,reverse,nil,nil,why);return finish(nil,why)
 end
 if not raw then
  local backwards={point(b)};local id=goal
  while true do
   backwards[#backwards+1]={mapID=a.mapID,x=(id%z.w+.5)/z.w,y=(floor(id/z.w)+.5)/z.h}
   if #backwards%256==0 and T.Checkpoint then T.Checkpoint() end
   if id==start then break end;id=previous[id]
  end
  backwards[#backwards+1]=point(a);raw=pathCopy(backwards,true)
 end
 local result={raw[1]};local at=1;local length=0;local shortcuts=0
 if A.PlanningJob then A.PlanningJob.Report('Smoothing the walking route') end
 local costs={0}
 if roads then for i=2,#raw do
  costs[i]=costs[i-1]+weighted(raw[i-1],raw[i])
  if i%256==0 and T.Checkpoint then T.Checkpoint() end
 end end
 -- Bounded lookahead smooths grid stairs without quadratic path scans. Every
 -- accepted shortcut uses the same supercover predicate as route validation.
 while at<#raw do
  local nextIndex=at+1
  for i=min(#raw,at+64),at+2,-1 do
   shortcuts=shortcuts+1;if shortcuts%16==0 and T.Checkpoint then T.Checkpoint() end
   if segment(z,raw[at],raw[i]) and (not roads or weighted(raw[at],raw[i])<=costs[i]-costs[at]+.000001) then nextIndex=i;break end
  end
  if not segment(z,raw[at],raw[nextIndex]) then return finish(nil,'unreachable') end
  length=length+yards(z,raw[at],raw[nextIndex]);result[#result+1]=raw[nextIndex];at=nextIndex
 end
 -- Bound retained geometry as well as cache entry count.
 if #result<=1024 then remember(key,reverse,result,length) end
 if maxDistance and length>maxDistance+.000001 then return finish(nil,'too long') end
 return finish(result,length)
end
function T.Distance(a,b,options)
 local path,length=T.Path(a,b,options);if not path then return nil,length end;return length
end
local function routeShape(route)
 if type(route)~='table' or type(route.points)~='table' or #route.points==0 then return false end
 local n=#route.points
 for k in pairs(route.points) do if type(k)~='number' or k%1~=0 or k<1 or k>n then return false end end
 for i=1,n do if not position(route.points[i]) then return false end end
 return true
end
function T.Validate(route,options)
 if not routeShape(route) then return false,'invalid route' end
 local points=route.points
 for i,p in ipairs(points) do
  if not T.Segment(p,p,options) then return false,'blocked endpoint' end
  if i>1 and not T.Segment(points[i-1],p,options) then return false,'blocked segment' end
  if i%64==0 and T.Checkpoint then T.Checkpoint() end
 end
 if route.loop and #points>1 and not T.Segment(points[#points],points[1],options) then return false,'blocked closure' end
 return true
end
function T.Route(route,options)
 if not routeShape(route) then return nil,'invalid route' end
 local original=route.points;local expanded={}
 for i,p in ipairs(original) do
  if not position(p) then return nil,'invalid point' end
  if not T.Segment(p,p,options) then return nil,T.Zone(p.mapID) and 'blocked endpoint' or 'unavailable' end
  expanded[#expanded+1]=copy(p)
  local target=original[i+1] or (route.loop and #original>1 and original[1])
  if target then
   local path,reason=T.Path(p,target,options);if not path then return nil,reason end
   for j=2,#path-1 do
    local bend=point(path[j]);bend.kind='travel';bend.mandatory=true;bend.navigation=true;expanded[#expanded+1]=bend
   end
  end
  if i%64==0 and T.Checkpoint then T.Checkpoint() end
 end
 local result={};for k,v in pairs(route) do if k~='points' then result[k]=copy(v) end end
 result.points=expanded;result.terrainVersion=1
 local valid,reason=T.Validate(result,options);if not valid then return nil,reason end
 return result
end
