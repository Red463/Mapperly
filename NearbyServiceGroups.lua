local _, A = ...
local G = {}
A.NearbyServiceGroups = G

local media = 'Interface\\AddOns\\Mapperly\\Media\\'
local roles = {
    {key='vendor', label='Vendors', icon=media..'Toolbar\\Small\\Services'},
    {key='repair', label='Gear repairs', icon='Interface\\Icons\\INV_Hammer_20'},
    {key='trainer', label='Trainers', icon=media..'Markers\\Small\\Note'},
    {key='inn', label='Innkeepers', icon=media..'Markers\\Small\\Hearthstone'},
    {key='flight', label='Flight masters', icon=media..'Markers\\Small\\FlightMaster'},
    {key='mail', label='Mailboxes', icon=media..'Markers\\Small\\Mail'},
}

-- Actual item art takes precedence. These classic icons also work when the
-- snapshot has an item name/class but no display icon.
local goods = {
    {'arrows', 'Arrows', 'INV_Ammo_Arrow_01'},
    {'bullets', 'Bullets', 'INV_Ammo_Bullet_02'},
    {'food', 'Food', 'INV_Misc_Food_11'},
    {'drink', 'Drink', 'INV_Drink_07'},
    {'bags', 'Bags', 'INV_Misc_Bag_10'},
    {'supplies', 'Trade supplies', 'INV_Fabric_Linen_01'},
    {'reagents', 'Reagents', 'INV_Misc_Dust_01'},
    {'equipment', 'Weapons and armour', 'INV_Sword_04'},
    {'fishing', 'Fishing supplies', 'INV_Fishingpole_02'},
    {'recipes', 'Recipes', 'INV_Scroll_03'},
    {'consumables', 'Consumables', 'INV_Potion_51'},
    {'mounts', 'Mounts', 'Ability_Mount_RidingHorse'},
    {'pets', 'Pets', 'Ability_Hunter_BeastTaming'},
    {'other', 'Other goods', 'INV_Misc_Box_01'},
}
local goodsByKey = {}
for order, group in ipairs(goods) do
    goodsByKey[group[1]] = {label=group[2], icon='Interface\\Icons\\'..group[3], order=order}
end

-- The specialties below are names on Forever NPC templates. Match the
-- profession at any rank and keep the exact title on the provider row.
-- Icon IDs come from the Forever client's SkillLine.SpellIconFileID.
local trainerTypes = {
    {'Alchemy', 136240, 'alchem'}, {'Blacksmithing', 136241, 'blacksmith', 'armorsmith', 'weaponsmith'},
    {'Cooking', 133971, 'cook'}, {'Enchanting', 136244, 'enchant'},
    {'Engineering', 136243, 'engineer'}, {'First Aid', 135966, 'first aid', 'physician', 'medic'},
    {'Fishing', 136245, 'fish'}, {'Herbalism', 136246, 'herbal'},
    {'Leatherworking', 136247, 'leather'}, {'Mining', 136248, 'mining', 'miner'},
    {'Skinning', 134366, 'skinn'}, {'Tailoring', 136249, 'tailor'},
    {'Riding', 132164, 'riding'}, {'Weapon training', 136235, 'weapon master'},
    {'Pet training', 132164, 'pet trainer'}, {'Portals', 135932, 'portal trainer'},
    {'Druid', 136096, 'druid'}, {'Hunter', 132164, 'hunter'}, {'Mage', 135846, 'mage'},
    {'Paladin', 135873, 'paladin'}, {'Priest', 135920, 'priest'}, {'Rogue', 132292, 'rogue'},
    {'Shaman', 136048, 'shaman'}, {'Warlock', 136186, 'warlock'}, {'Warrior', 132292, 'warrior'},
}
local function trainerType(detail, fallbackIcon)
    local title = detail:lower()
    for _, spec in ipairs(trainerTypes) do
        for index = 3, #spec do
            if title:find(spec[index], 1, true) then return spec[1], spec[2] end
        end
    end
    return detail, fallbackIcon
end

local stockCatalog, stockByNPC
local function inventory(npcID)
    local catalog = A.VendorGoods
    if not catalog or not npcID or not catalog.stock[npcID] then return end
    if catalog ~= stockCatalog then stockCatalog, stockByNPC = catalog, {} end
    if not stockByNPC[npcID] then
        local buckets = {}
        for _, id in ipairs(catalog.stock[npcID]) do
            local item = catalog.items[id]
            if item and item[2] then
                local key = goodsByKey[item[1]] and item[1] or 'other'
                local bucket = buckets[key]
                if not bucket then bucket = {}; buckets[key] = bucket end
                bucket[#bucket+1] = item
            end
        end
        stockByNPC[npcID] = buckets
    end
    return stockByNPC[npcID]
end

local function matches(terms, base, itemName)
    for _, term in ipairs(terms) do
        if not base:find(term, 1, true) and not (itemName and itemName:find(term, 1, true)) then return false end
    end
    return true
end

local function addCategory(group, lookup, id, label, order, provider)
    local category = lookup[id]
    if not category then
        category = {key=group.key..':'..id, label=label, order=order, icon=provider.icon, providers={}}
        lookup[id] = category
        group.categories[#group.categories+1] = category
    end
    -- The snapshot already sorts its services by distance, then name and key.
    category.providers[#category.providers+1] = provider
end

local function addVendor(group, lookup, service, terms, base, fallbackIcon)
    local buckets = inventory(service.npcID)
    if not buckets or not next(buckets) then
        local label = 'Other vendors'
        if #terms == 0 or matches(terms, base..' '..label:lower()) then
            addCategory(group, lookup, 'unlisted', label, #goods+1, {
                service=service, example=service.detail, icon=fallbackIcon, subtitle=service.name..' · '..service.detail,
            })
        end
        return
    end
    for key, items in pairs(buckets) do
        local typeInfo = goodsByKey[key]
        local item = items[1]
        if #terms > 0 then
            local searchText = base..' '..typeInfo.label:lower()
            if not matches(terms, searchText) then
                item = nil
                for _, candidate in ipairs(items) do
                    if matches(terms, searchText, candidate[2]:lower()) then item = candidate; break end
                end
            end
        end
        if item then
            local icon = type(item[3]) == 'number' and item[3] > 0 and item[3] or typeInfo.icon
            addCategory(group, lookup, key, typeInfo.label, typeInfo.order, {
                service=service, example=item[2], icon=icon, subtitle=service.name..' · '..item[2],
            })
        end
    end
end

local previousSnapshot, previousCatalog, previousSearch, previousGroups

function G.List(query)
    local snapshot, zone, reason = A.NearbyServices.ListByRole()
    if not snapshot then return {}, zone, reason end
    local search = (query or ''):lower():match('^%s*(.-)%s*$')
    if snapshot == previousSnapshot and A.VendorGoods == previousCatalog and search == previousSearch then
        return previousGroups, zone, reason
    end
    local terms, groups = {}, {}
    for term in search:gmatch('%S+') do terms[#terms+1] = term end
    for _, role in ipairs(roles) do
        local group = {key=role.key, label=role.label, categories={}}
        local lookup = {}
        for _, service in ipairs(snapshot[role.key]) do
            local base = #terms > 0 and (role.label..' '..service.name..' '..service.detail):lower()
            if role.key == 'vendor' then
                addVendor(group, lookup, service, terms, base, role.icon)
            elseif role.key == 'trainer' then
                local label, icon = trainerType(service.detail, role.icon)
                if #terms == 0 or matches(terms, base..' '..label:lower()) then
                    addCategory(group, lookup, label, label, 0, {
                        service=service, example=service.detail, icon=icon, subtitle=service.name..' · '..service.detail,
                    })
                end
            elseif #terms == 0 or matches(terms, base) then
                addCategory(group, lookup, service.key, service.name, 0, {
                    service=service, example=service.detail, icon=role.icon, subtitle=service.detail,
                })
            end
        end
        if #group.categories > 0 then
            if role.key == 'trainer' or role.key == 'vendor' then
                table.sort(group.categories, function(a, b)
                    if a.order ~= b.order then return a.order < b.order end
                    return a.label < b.label
                end)
            end
            groups[#groups+1] = group
        end
    end
    previousSnapshot, previousCatalog, previousSearch, previousGroups = snapshot, A.VendorGoods, search, groups
    return groups, zone, reason
end
