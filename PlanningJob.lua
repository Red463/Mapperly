local _,A=...
local J={};A.PlanningJob=J
local active,frame
local function readClock(timer,factor)
    if type(timer)~='function' then return end
    local ok,n=pcall(timer)
    if ok and not (issecretvalue and issecretvalue(n)) and type(n)=='number' and n==n and math.abs(n)<math.huge then return n*factor end
end
local function clock()
    return readClock(debugprofilestop,1) or readClock(GetTimePreciseSec,1000) or readClock(GetTime,1000) or 0
end
function J.Cancel() active=nil end
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
    if not ok or coroutine.status(job.thread)=='dead' then
        active=nil
        if ok and result then
            if job.done then
                -- Work has finished; protecting its non-yielding UI callback is
                -- safe here and prevents hidden widget errors leaving 'Planning'.
                local displayed,errorText=pcall(job.done,result)
                if not displayed and job.failed then job.failed('The route was calculated, but displaying it failed: '..tostring(errorText)) end
            end
        elseif job.failed then job.failed(ok and reason or tostring(result)) end
    end
end
function J.Start(work,done,failed)
    J.Cancel()
    active={thread=coroutine.create(work),done=done,failed=failed}
    if not frame then
        frame=CreateFrame('Frame',nil,UIParent)
        frame:SetSize(1,1);frame:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);frame:EnableMouse(false)
        frame:SetScript('OnUpdate',J.Step);frame:Show()
    end
    return true
end
