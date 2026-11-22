local _,A=...
local J={};A.PlanningJob=J
local active,frame
local function clock()
    if debugprofilestop then return debugprofilestop() end
    return 0
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
        if ok and result then if job.done then job.done(result) end
        elseif job.failed then job.failed(ok and reason or tostring(result)) end
    end
end
function J.Start(work,done,failed)
    J.Cancel()
    active={thread=coroutine.create(work),done=done,failed=failed}
    if not frame then frame=CreateFrame('Frame');frame:SetScript('OnUpdate',J.Step) end
    return true
end
