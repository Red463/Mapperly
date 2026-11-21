local _,A=...
A.revealTextures={}
local function padded(n) local p=16;while p<n do p=p*2 end;return p end
function A.RefreshReveal()
    for _,t in ipairs(A.revealTextures) do t:Hide() end
    if not A.db.reveal or not C_Map.GetMapArtID or not C_Map.GetMapArtLayers then return end
    local map=A.map:GetMapID();if not map then return end
    local art=C_Map.GetMapArtID(map);local data=A.MapReveal and A.MapReveal[art]
    local layers=C_Map.GetMapArtLayers(map);local layer=layers and layers[1]
    if not data or not layer then return end
    local explored={}
    if C_MapExplorationInfo and C_MapExplorationInfo.GetExploredMapTextures then
        for _,v in ipairs(C_MapExplorationInfo.GetExploredMapTextures(map) or {}) do explored[v.textureWidth..':'..v.textureHeight..':'..v.offsetX..':'..v.offsetY]=true end
    else return end
    local canvas=A.map:GetCanvas();local n=0
    for key,ids in pairs(data) do if not explored[key] then
        local w,h,x,y=key:match('^(%d+):(%d+):(%d+):(%d+)$');w,h,x,y=tonumber(w),tonumber(h),tonumber(x),tonumber(y)
        if w then
            local files={};for id in ids:gmatch('%d+') do files[#files+1]=tonumber(id) end
            local tw,th=layer.tileWidth,layer.tileHeight;local cols=math.ceil(w/tw)
            for row=0,math.ceil(h/th)-1 do for col=0,cols-1 do
                local file=files[row*cols+col+1]
                if file then
                    n=n+1;local t=A.revealTextures[n]
                    if not t then t=canvas:CreateTexture(nil,'ARTWORK',nil,-7);A.revealTextures[n]=t end
                    local cw,ch=math.min(tw,w-col*tw),math.min(th,h-row*th)
                    t:SetTexture(file);t:SetVertexColor(.65,.65,.65);t:ClearAllPoints()
                    t:SetPoint('TOPLEFT',canvas,'TOPLEFT',(x+col*tw)/layer.layerWidth*canvas:GetWidth(),-(y+row*th)/layer.layerHeight*canvas:GetHeight())
                    t:SetSize(cw/layer.layerWidth*canvas:GetWidth(),ch/layer.layerHeight*canvas:GetHeight())
                    t:SetTexCoord(0,cw/padded(cw),0,ch/padded(ch));t:Show()
                end
            end end
        end
    end end
end
