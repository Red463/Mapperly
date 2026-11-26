"""Join outdoor Forever vendors' regular stock to the matching client item data."""
import argparse
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
import subprocess

import build_quest_catalog as catalog
import build_quest_locations as locations
import build_service_directory as directory
import build_services as services


# English CSV exports from the unmodified 1.60.1.70959 DB2s. See VendorGoods-SOURCES.
CSV_SHA256 = {
    'item': '5ba450e67ec2fa4d9791727c7bd7ec70ff87e22aa4f14b35f6e8fd2324575c03',
    'itemsparse': '42c4fcde53c7ffe8641f3fe982098cdb18bd2928cc14c4facf6b0c0a34764cfa',
    'itemxitemeffect': '33c4993cdeeddeab613f3f0a2921f225693401120384f98c7ec2180803e519d6',
    'itemeffect': '2f78aeca3c348e76333be977d3d04c19d6f248376969764b91a544f21e4c1fd1',
    'spellname': '920c68116ec24baae058d97db6da2b4c8af06a4a603d3e524cf73ec2c49b91ae',
}


def regular_stock(rows, vendor_ids):
    stock = defaultdict(set)
    conditional = set()
    for table, row in rows:
        if table == 'conditions':
            if int(row['SourceTypeOrReferenceId']) == 23:  # CONDITION_SOURCE_TYPE_NPC_VENDOR
                conditional.add((int(row['SourceGroup']), int(row['SourceEntry'])))
            continue
        vendor_id, item_id = int(row['entry']), int(row['item'])
        if vendor_id in vendor_ids and int(row['type']) == 1 and item_id > 0 and not int(row['PlayerConditionID']):
            stock[vendor_id].add(item_id)
    for vendor_id, item_id in conditional:
        if vendor_id in stock:
            stock[vendor_id].discard(item_id)
    return {vendor: goods for vendor, goods in stock.items() if goods}


def category(item_class, subclass, food_type, use_effects, item_id=0):
    # Fishing poles are weapons in Item.db2. The five classic lures below
    # cast verified temporary fishing-pole enchants (see data provenance).
    if (item_class, subclass) == (2, 20) or item_class == 0 and item_id in {6529, 6530, 6532, 6533, 6811}:
        return 'fishing'
    if (item_class, subclass) == (2, 14) and item_id in {2901, 5956, 7005}:
        return 'supplies'  # Mining Pick, Blacksmith Hammer and Skinning Knife.
    if item_class == 0 and subclass == 5:
        # Food and drinks share one item subclass. Legacy consumables use
        # recovery categories 11/59; newer Forever consumables can use category 0.
        if any(cat == 59 or name == 'Drink' or name.endswith(' Alcohol') for cat, name in use_effects):
            return 'drink'
        if food_type or any(cat == 11 or name in ('Food', 'Nutritious Food') for cat, name in use_effects):
            return 'food'
    if item_class == 6:
        return {2: 'arrows', 3: 'bullets'}.get(subclass, 'other')
    if item_class == 15:
        return {1: 'reagents', 2: 'pets', 5: 'mounts'}.get(subclass, 'other')
    return {0: 'consumables', 1: 'bags', 2: 'equipment', 4: 'equipment', 5: 'reagents',
            7: 'supplies', 9: 'recipes', 11: 'bags'}.get(item_class, 'other')


def csv_rows(name, path):
    locations.verify(path, CSV_SHA256[name])
    with path.open(encoding='utf-8-sig', newline='') as file:
        yield from csv.DictReader(file)


def load_items(item_ids, client_rows, hotfix_rows):
    item_data = {}
    names = {}
    for row in client_rows('item'):
        item_id = int(row['ID'])
        if item_id in item_ids:
            item_data[item_id] = row
    for row in client_rows('itemsparse'):
        item_id = int(row['ID'])
        if item_id in item_ids and row['Display_lang']:
            names[item_id] = row['Display_lang']
    # These SQL records predate build 70959. Use them only for missing base facts.
    for table, row in hotfix_rows:
        item_id = int(row['ID'])
        if item_id in item_ids:
            if table == 'item':
                item_data.setdefault(item_id, row)
            elif row.get('Display'):
                names.setdefault(item_id, row['Display'])

    links = defaultdict(set)
    for row in client_rows('itemxitemeffect'):
        item_id = int(row['ItemID'])
        if item_id in item_ids:
            links[int(row['ItemEffectID'])].add(item_id)
    spell_links = defaultdict(list)
    for row in client_rows('itemeffect'):
        effect = int(row['ID'])
        if effect in links and int(row['TriggerType']) == 0 and not int(row['PlayerConditionID']):
            for item_id in links[effect]:
                spell_links[int(row['SpellID'])].append((item_id, int(row['SpellCategoryID'])))
    spell_names = {int(r['ID']): r['Name_lang'] for r in client_rows('spellname') if int(r['ID']) in spell_links}
    uses = defaultdict(list)
    for spell_id, link in spell_links.items():
        for item_id, spell_category in link:
            uses[item_id].append((spell_category, spell_names.get(spell_id, '')))
    items = {}
    for item_id, row in item_data.items():
        icon = int(row['IconFileDataID'])
        if item_id in names and icon > 0:
            kind = category(int(row['ClassID']), int(row['SubclassID']), int(row['ItemPetFoodID']), uses[item_id], item_id)
            items[item_id] = (kind, names[item_id], icon)
    return items


def render(stock, items):
    lines = ['-- Generated by tools/build_vendor_goods.py. See VendorGoods-SOURCES.md.',
             '-- Forever TDB 2026-10-14 and Forever client 70959 (enUS).', 'local _, A = ...',
             'A.VendorGoods = {items={']
    for item_id, (kind, name, icon) in sorted(items.items()):
        lines.append(f' [{item_id}]={{"{kind}",{json.dumps(name, ensure_ascii=False)},{icon}}},')
    lines.append('},stock={')
    for vendor, goods in sorted(stock.items()):
        known = sorted(goods.intersection(items))
        if known:
            lines.append(f' [{vendor}]={{{",".join(map(str, known))}}},')
    lines.append('}}')
    return '\n'.join(lines) + '\n'


def build(tables, spell_names):
    vendor_ids = {r['id'] for records in directory.load_directory().values() for r in records if r['category'] == 'vendor'}
    world = services.CACHE / services.WORLD
    hotfix = services.CACHE / services.HOTFIX
    if not hotfix.exists():
        subprocess.run(['tar', '-xf', str(services.CACHE / services.ARCHIVE), '-C', str(services.CACHE), hotfix.name], check=True)
    locations.verify(hotfix, catalog.HOTFIX_SHA256)
    stock = regular_stock(services.rows(world, {'npc_vendor', 'conditions'}), vendor_ids)
    item_ids = set().union(*stock.values())
    def client_rows(name):
        return csv_rows(name, spell_names if name == 'spellname' else tables / (name + '.csv'))
    items = load_items(item_ids, client_rows, services.rows(hotfix, {'item', 'item_sparse'}))
    output = render(stock, items)
    (services.ROOT / 'Data/VendorGoods.lua').write_text(output, encoding='utf-8', newline='\n')
    print(f'{sum(bool(goods.intersection(items)) for goods in stock.values())}/{len(vendor_ids)} vendor identities; '
          f'{len(items)}/{len(item_ids)} distinct stock items have a verified name, classification and icon. '
          f'{sum(len(goods.intersection(items)) for goods in stock.values())} vendor-item pairs.')
    print(dict(sorted(Counter(row[0] for row in items.values()).items())))


if __name__ == '__main__':
    snapshot = services.ROOT.parent / 'output/forever-datamine-70959'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables', type=Path, default=snapshot / 'vendor-goods')
    parser.add_argument('--spell-names', type=Path, default=snapshot / 'raw/dbfilesclient/spellname.csv')
    args = parser.parse_args()
    build(args.tables, args.spell_names)
