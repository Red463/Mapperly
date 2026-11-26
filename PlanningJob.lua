local _,A=...
local J={};A.PlanningJob=J
local active,frame
local serial=0
local results={}
local function scalar(v)
    if issecretvalue and issecretvalue(v) then return end
    if type(v)=='string' then return v:sub(1,320) end
    if type(v)=='boolean' then return v end
    if type(v)=='number' and v==v and math.abs(v)<math.huge then return v end
end
local function copy(source,keys)
    local out={};if type(source)=='table' then for _,key in ipairs(keys) do out[key]=scalar(source[key]) end end;return out
end
local counterKeys={'id','stage','paths','cells','slices','workMS','peakSliceMS','mapID','checked','total','flightRoutes','flightSources','cacheHits','cacheMisses','source','waterCells','waterUnknown','waterRejected'}
local positionKeys={'map','mapID','x','y'}
local destinationKeys={'map','mapID','x','y','walkingOnly'}
local function position(p,keys)
    if not (issecretvalue and issecretvalue(p)) and type(p)=='table' then return copy(p,keys) end
end
function J.Recent()
    local out={}
    for i,row in ipairs(results) do
        out[i]=copy(row,{'state','elapsedMS','reason','kind','coverage','source','distance'})
        out[i].progress=copy(row.progress,counterKeys)
        out[i].start=position(row.start,positionKeys);out[i].destination=position(row.destination,destinationKeys)
    end
    return out
end
function J.Progress()
    if not active then return end
    local p={};for k,v in pairs(active.progress) do p[k]=v end;return p
end
function J.Report(stage,details)
    if not active then return end
    if active.progress.stage~=stage then active.progress.checked=nil;active.progress.total=nil end
    active.progress.stage=stage
    for k,v in pairs(details or {}) do active.progress[k]=v end
end
function J.BeginPath(map)
    if not active then return end
    local p=active.progress;p.paths=p.paths+1;p.mapID=map;p.stage='Finding a walking path';p.lastCells=0;p.checked=nil;p.total=nil
end
function J.PathProgress(count)
    if not active then return end
    local p=active.progress;p.cells=p.cells+math.max(0,count-p.lastCells);p.lastCells=count
end
local function readClock(timer,factor)
    if type(timer)~='function' then return end
    local ok,n=pcall(timer)
    if ok and not (issecretvalue and issecretvalue(n)) and type(n)=='number' and n==n and math.abs(n)<math.huge then return n*factor end
end
local function clock()
    return readClock(debugprofilestop,1) or readClock(GetTimePreciseSec,1000) or readClock(GetTime,1000) or 0
end
local function record(job,state,result,reason)
    local row={state=state,elapsedMS=math.max(0,clock()-(job.started or clock())),reason=scalar(reason),progress=copy(job.progress,counterKeys),start=job.start,destination=job.destination}
    if type(result)=='table' then for _,key in ipairs({'kind','coverage','source','distance'}) do row[key]=scalar(result[key]) end end
    results[#results+1]=row;while #results>6 do table.remove(results,1) end
    return row
end
function J.Cancel() if active then record(active,'cancelled') end;active=nil end
function J.IsRunning() return active~=nil end
function J.Checkpoint()
    local job=active
    if not job then return end
    job.checkpoints=job.checkpoints+1
    if job.checkpoints>=8 or clock()-job.began>=4 then coroutine.yield() end
end
function J.Step()
    local job=active;if not job then return end
    job.began=clock();job.checkpoints=0
    local previous=A.Terrain and A.Terrain.Checkpoint
    if A.Terrain then A.Terrain.Checkpoint=J.Checkpoint end
    local ok,result,reason=coroutine.resume(job.thread)
    if A.Terrain then A.Terrain.Checkpoint=previous end
    if active~=job then return end
    local duration=math.max(0,clock()-job.began)
    local progress=job.progress
    progress.slices=progress.slices+1
    progress.workMS=progress.workMS+duration
    progress.peakSliceMS=math.max(progress.peakSliceMS,duration)
    if not ok or coroutine.status(job.thread)=='dead' then
        local row=record(job,ok and result and 'ready' or 'failed',result,ok and reason or result)
        active=nil
        if ok and result then
            if job.done then
                -- Work has finished; protecting its non-yielding UI callback is
                -- safe here and prevents hidden widget errors leaving 'Planning'.
                local displayed,errorText=pcall(job.done,result)
                if not displayed then
                    local message='The route was calculated, but displaying it failed: '..tostring(errorText)
                    row.state='failed';row.reason=scalar(message)
                    if job.failed then job.failed(message) end
                end
            end
        elseif job.failed then job.failed(ok and reason or tostring(result)) end
    end
end
function J.Start(work,done,failed,target,start)
    J.Cancel()
    serial=serial+1
    active={thread=coroutine.create(work),done=done,failed=failed,started=clock(),start=position(start,positionKeys),destination=position(target,destinationKeys),
        progress={id=serial,stage='Preparing route',paths=0,cells=0,lastCells=0,slices=0,workMS=0,peakSliceMS=0}}
    if not frame then
        frame=CreateFrame('Frame',nil,UIParent)
        frame:SetSize(1,1);frame:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);frame:EnableMouse(false)
        frame:SetScript('OnUpdate',J.Step);frame:Show()
    end
    return true
end
