local _,A=...
-- Native ADT liquid occupancy is conservative: a wet cell can contain a
-- bridge, but only a separate certified native-floor corridor can prove it.
local W={};A.Water=W
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local planning=setmetatable({},{__mode='k'})
local main={}
-- A yielding search owns its policy; UI, arrival checks and newer jobs do not.
function W.WithPlanningPolicy(allowed,work)
 local thread=coroutine.running();local key=thread or main
 local previous=planning[key];planning[key]=allowed
 if thread then
  local result,reason=work();planning[key]=previous;return result,reason
 end
 local ok,result,reason=pcall(work);planning[key]=previous
 if not ok then error(result,0) end
 return result,reason
end
local bits={};for i=1,#alphabet do bits[alphabet:byte(i)]=i-1 end
function W.AllowSwimming(options)
 if type(options)=='table' and type(options.allowSwimming)=='boolean' then return options.allowSwimming end
 local policy=planning[coroutine.running() or main]
 if policy~=nil then return policy end
 return not (A.db and A.db.allowSwimming==false)
end
function W.Zone(map,z)
 if type(z)~='table' then return end
 local data=A.WaterData
 local water=type(data)=='table' and data.version==1 and type(data.zones)=='table' and data.zones[map]
 if type(water)=='table' and type(water.baseSha256)=='string' and water.w==z.w and water.h==z.h and water.baseSha256==z.maskSha256 and type(water.rows)=='table' then return water end
end
function W.Cell(water,x,y)
 if not water or x<0 or y<0 or x>=water.w or y>=water.h then return false end
 local row=water.rows[y+1];local value=type(row)=='string' and bits[row:byte(math.floor(x/6)+1)]
 return value and math.floor(value/2^(5-x%6))%2==1 or false
end
