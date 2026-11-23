local _,A=...
local C={};A.CityNavigation=C
-- Ironforge's playable WMO floors do not match the outdoor terrain beneath
-- and above them. This is explicit city wayfinding, not a terrain-mask edit.
function C.Supports(p,options)
 if type(p)~='table' or options and options.walkingOnly then return false end
 if issecretvalue and issecretvalue(p.mapID) then return false end
 return p.mapID==1455 and A.ValidPin({map=p.mapID,x=p.x,y=p.y,name='City navigation'}) and A.Terrain.Zone(p.mapID)~=nil
end
function C.Path(from,to,options)
 if not C.Supports(from,options) or not C.Supports(to,options) or from.mapID~=to.mapID then return end
 local z=A.Terrain.Zone(from.mapID)
 local length=math.sqrt(((from.x-to.x)*z.widthYards)^2+((from.y-to.y)*z.heightYards)^2)
 local points={{mapID=from.mapID,x=from.x,y=from.y},{mapID=to.mapID,x=to.x,y=to.y}}
 points.cityGuidance=true;points.cityInstruction='Walk through Ironforge'
 return points,length
end
