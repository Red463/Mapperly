local _,A=...
local function build()
    local U=A.Dialogs
    local f=U.Window('MapperlyNoteWindow','Map notes','Keep useful places, reminders and meeting points.',640,736);A.noteWindow=f
    f.editor=U.Card(f,24,132,592,504);f.browser=U.Card(f,24,132,592,536);f.browser:Hide()
    f.place=U.Label(f.editor,'',16,14,'GameFontNormal');f.place:SetWidth(558);f.place:SetWordWrap(false)
    U.Label(f.editor,'Name',16,46,'GameFontNormal');f.nameInput=U.Input(f.editor,20,68,550,28,120)
    U.Label(f.editor,'Group (optional)',16,108,'GameFontNormal');f.groupInput=U.Input(f.editor,20,130,550,28,40)
    U.Label(f.editor,'Description (optional)',16,170,'GameFontNormal')
    local descriptionCard=U.Card(f.editor,16,192,558,90)
    local scroll=CreateFrame('ScrollFrame',nil,descriptionCard,'UIPanelScrollFrameTemplate');scroll:SetPoint('TOPLEFT',descriptionCard,'TOPLEFT',8,-4);scroll:SetSize(518,78)
    f.descriptionInput=U.Input(scroll,0,0,512,78,1000,true);scroll:SetScrollChild(f.descriptionInput)
    f.descriptionInput:SetScript('OnCursorChanged',function(_,_,y,_,height)
        local top=scroll:GetVerticalScroll();local cursor=-y
        if cursor<top then scroll:SetVerticalScroll(cursor) elseif cursor+height>top+78 then scroll:SetVerticalScroll(cursor+height-78) end
    end)
    U.Label(f.editor,'Map icon',16,296,'GameFontNormal');f.iconButtons={}
    U.Label(f.editor,'Use any symbol for any purpose.',176,296,'GameFontDisableSmall')
    f.selectedPreview=f.editor:CreateTexture(nil,'ARTWORK');f.selectedPreview:SetSize(24,24);f.selectedPreview:SetPoint('TOPRIGHT',f.editor,'TOPRIGHT',-18,-288)
    local function selectIcon(key)
        f.selectedIcon=key
        A.SetPinTexture(f.selectedPreview,key,nil,24)
        for k,b in pairs(f.iconButtons) do b.active=k==key;b:UpdateVisual() end
    end
    for i,key in ipairs(A.noteIcons) do
        local k=key
        local b=U.Action(f.editor,'',16+((i-1)%6)*92,320+math.floor((i-1)/6)*64,86,function() selectIcon(k) end);b:SetSize(86,58)
        b.preview=b:CreateTexture(nil,'ARTWORK');b.preview:SetSize(30,30);b.preview:SetPoint('CENTER',b,'CENTER',0,0);A.SetPinTexture(b.preview,k,nil,30)
        A.AttachButtonTooltip(b,'Select this symbol for your note');f.iconButtons[k]=b
    end
    f.error=U.Label(f.editor,'',16,470,'GameFontRedSmall');f.error:SetWidth(558)
    local function refresh() A.db.filters.notes=true;if A.Refresh then A.Refresh() end end
    local function save()
        local fields={name=f.nameInput:GetText(),group=f.groupInput:GetText(),description=f.descriptionInput:GetText(),icon=f.selectedIcon}
        local note
        if f.editing then
            local exists=false;for _,p in ipairs(A.db.notes) do if p==f.editing then exists=true;break end end
            if not exists then f.error:SetText('This note was removed. Reopen the note editor.');return end
            note=A.UpdateNote(f.editing,fields)
        else note=A.AddNote(f.targetMap,f.x,f.y,fields.name,fields) end
        if not note then f.error:SetText('Enter a name and a valid map location.');return end
        refresh();f:Hide()
    end
    f.save=U.Action(f,'Save note',24,684,120,save)
    if A.Theme then A.Theme.ButtonRole(f.save,'primary') end
    f.navigate=U.Action(f,'Navigate',154,684,110,function()
        local name=f.nameInput:GetText();if name:match('^%s*$') then name='Map note' end
        local ok,reason=A.Navigation.ToPin({map=f.targetMap,x=f.x,y=f.y,name=name})
        if ok then f:Hide() else f.error:SetText(reason) end
    end)
    f.delete=U.Action(f,'Delete note',274,684,120,function()
        if f.editing then A.RemoveNote(f.editing);refresh();f:Hide() end
    end)
    U.Action(f,'Cancel',506,684,110,function() f:Hide() end)
    U.Label(f.browser,'Search names, groups, descriptions or zones',14,12,'GameFontDisableSmall')
    f.search=U.Input(f.browser,18,34,548,28,120);f.library=U.List(f.browser,10,80,568,440)
    f.empty=U.Label(f.browser,'',20,100,'GameFontDisableSmall')
    local function renderNotes()
        local records={};local query=f.search:GetText():lower()
        for _,p in ipairs(A.db.notes) do if A.ValidPin(p) then
            local info=C_Map.GetMapInfo and C_Map.GetMapInfo(p.map)
            local text=p.name..' '..(p.group or '')..' '..(p.description or '')..' '..(info and info.name or '')
            if text:lower():find(query,1,true) then records[#records+1]=p end
        end end
        table.sort(records,function(a,b)
            local ga,gb=(a.group or ''):lower(),(b.group or ''):lower()
            if ga~=gb then return ga<gb end;return a.name:lower()<b.name:lower()
        end)
        f.empty:SetText(#records==0 and 'No matching notes.' or '')
        f.library:Render(records,function(row,p)
            A.SetPinTexture(row.icon,p.icon or 'notes',nil,24);row.title:SetText(p.name)
            local info=C_Map.GetMapInfo and C_Map.GetMapInfo(p.map)
            row.detail:SetText((p.group and p.group~='' and p.group..'  -  ' or '')..(info and info.name or 'Map '..p.map)..string.format('  %.1f, %.1f',p.x*100,p.y*100))
            if not row.open then row.open=U.Action(row,'Edit note',420,5,108,function() local n=row.record;A.ShowNote(n.map,n.x,n.y,n) end) end
        end)
    end
    local function select(page)
        U.Tabs(f.tabs,page);f.editor:SetShown(page=='edit');f.browser:SetShown(page=='browser')
        f.save:SetShown(page=='edit');f.navigate:SetShown(page=='edit');f.delete:SetShown(page=='edit' and f.editing~=nil)
        if page=='browser' then renderNotes() end
    end
    f.tabs={};f.tabs.edit=U.Action(f,'Edit note',24,88,170,function() select('edit') end)
    f.browserTab=U.Action(f,'My notes',202,88,170,function() select('browser') end);f.tabs.browser=f.browserTab
    f.search:SetScript('OnTextChanged',renderNotes)
    for _,e in ipairs({f.nameInput,f.groupInput,f.descriptionInput,f.search}) do e:SetScript('OnEscapePressed',function() f:Hide() end) end
    f.nameInput:SetScript('OnEnterPressed',save);f.groupInput:SetScript('OnEnterPressed',save)
    f.nameInput:SetScript('OnTabPressed',function() f.groupInput:SetFocus() end)
    f.groupInput:SetScript('OnTabPressed',function() f.descriptionInput:SetFocus() end)
    f.SelectPage=select;f.SelectIcon=selectIcon;return f
end
function A.ShowNote(map,x,y,note)
    local f=A.noteWindow or build();f.targetMap=map;f.x=x;f.y=y;f.editing=note
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    f.place:SetText(string.format('%s  -  %.1f, %.1f',info and info.name or 'Map '..tostring(map),x*100,y*100))
    f.nameInput:SetText(note and note.name or '');f.groupInput:SetText(note and note.group or '');f.descriptionInput:SetText(note and note.description or '')
    f.SelectIcon(note and note.icon or 'note_poi');f.error:SetText('');f.SelectPage('edit');A.Dialogs.Show(f);f.nameInput:SetFocus()
end
