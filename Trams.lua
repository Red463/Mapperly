local _,A=...
local T={};A.Trams=T
local function number(v) return not (issecretvalue and issecretvalue(v)) and type(v)=='number' and v==v and math.abs(v)<math.huge end
local function call(fn,...)
 if type(fn)~='function' then return end
 local ok,a,b,c,d=pcall(fn,...);if ok then return a,b,c,d end
end
local function conflict(ax,ay,bx,by)
 local squared=0
 if number(ax) and number(bx) then squared=squared+(ax-bx)^2 end
 if number(ay) and number(by) then squared=squared+(ay-by)^2 end
 return squared>=64
end
local function position(p)
 local n,e,z,i=call(UnitPosition,'player')
 local x,y,instance
 if p then x,y,instance=A.TravelNetwork.World(p) end
 local hbd=LibStub and LibStub('HereBeDragons-2.0',true)
 local wx,wy,wi
 if hbd then wx,wy,wi=call(hbd.GetPlayerWorldPosition,hbd) end
 -- Validate every readable source, even if native XY is protected while its
 -- instance is public. A stale city sample must not override a live station.
 if number(i) and number(wi) and i~=wi then return nil,nil,'conflict' end
 if number(i) and x and i~=instance or number(wi) and x and wi~=instance then return nil,nil,'conflict' end
 if conflict(e,n,x,y) then return nil,nil,'conflict' end
 if conflict(wx,wy,x,y) then return nil,nil,'conflict' end
 if conflict(e,n,wx,wy) then return nil,nil,'conflict' end
 local actual=number(i) and i or number(wi) and wi or instance
 if actual~=nil then return actual,number(z) and z or nil end
end
local function onFoot()
 if A.Flights and A.Flights.worldReady==false then return false end
 for _,row in ipairs({{UnitOnTaxi,'player'},{UnitInVehicle,'player'},{IsSwimming}}) do
  if type(row[1])=='function' then
   local value=call(row[1],row[2])
   if issecretvalue and issecretvalue(value) or value~=false then return false end
  end
 end
 return true
end
function T.CanDisembark(row,p,state)
 state.needsConfirmation=false
 if not state.interiorSeen or not p or not onFoot() then return false end
 local instance,z,reason=position(p)
 if reason or instance~=0 then return false end
 -- Entering the tram instance then emerging in the other city is the
 -- transition. No exact landing cell, altitude or exit-radius test is needed.
 local city=A.TravelNetwork.Transform(p,row.b.mapID)
 return city~=nil
end
function T.Inside()
 if A.Flights and A.Flights.worldReady==false then return false end
 return position()==369
end
function T.Guide(leg,p,state)
 if A.Flights and A.Flights.worldReady==false then return nil,'Waiting for the station or city to load...' end
 local row=leg.transport;local instance=position()
 if instance==row.interiorInstance then state.interiorSeen=true;state.departed=true end
 if T.CanDisembark(row,p,state) then return nil,nil,true end
 if state.interiorSeen then
  return nil,'Ride the tram and exit the '..row.toName..' portal.'
 end
 return p and A.Transports.Aim(row.board,p.mapID),'Walk through the '..row.fromName..' tram portal.'
end

-- City portal bearings do not change terrain permissions. Eligible tram
-- endpoints and their arrival neighbourhoods can request this fallback.
function T.Access(from,to,edges,allowed)
 if allowed==false then return end
 if from.mapID~=to.mapID or from.mapID~=1453 and from.mapID~=1455 then return end
 for _,edge in ipairs(edges or {}) do
  local row=edge.transport
  local leaving=row and row.automaticTram and from==edge.to
  if row and row.automaticTram and from.mapID==row.b.mapID then
   local distance=A.TravelNetwork.Distance(from,row.b)
   if distance and distance<=80 then leaving=true end
   -- A replan after leaving Stormwind's portal must not require another
   -- tram round trip to regain the same station-side walking component.
   if from.mapID==1453 and A.WalkingRegions then
    local current,station=A.WalkingRegions.Get(from),A.WalkingRegions.Get(row.b)
    if current and current==station and A.WalkingRegions.Get(to)~=current then leaving=true end
   end
  end
  if row and row.automaticTram and (to==edge.from or leaving) then
   local length=A.TravelNetwork.Distance(from,to)
   if length then
    local points={{mapID=from.mapID,x=from.x,y=from.y},{mapID=to.mapID,x=to.x,y=to.y}}
    points.portalGuidance=true
    points.portalInstruction=to==edge.from and 'Walk through the '..row.fromName..' tram portal' or 'Continue walking through '..row.toName
    return points,length
   end
  end
 end
end
