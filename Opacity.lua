local _,A=...
function A.UpdateOpacity(takeOwnership)
    local f=A.map
    if not f or not A.db then return end
    -- WorldMap OnShow registers a second, deferred movement fader. Remove both
    -- its active and pending registration before applying our own preferences.
    if takeOwnership and PlayerMovementFrameFader and PlayerMovementFrameFader.RemoveFrame then
        PlayerMovementFrameFader.RemoveFrame(f)
    end
    local moving
    if type(IsPlayerMoving)=='function' then moving=IsPlayerMoving()
    else moving=(GetUnitSpeed('player') or 0)>0 end
    local alpha=A.db.compact and (moving and A.db.movingAlpha or A.db.alpha) or 1
    if f:GetAlpha()~=alpha then f:SetAlpha(alpha) end
end
