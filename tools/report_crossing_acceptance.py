"""Generate per-zone live checks from the actual shipped handoffs and approaches."""
from pathlib import Path
import json
from audit_crossing_approaches import verify_inventory
ROOT=Path(__file__).resolve().parents[1]

def main():
    raw=(ROOT.parent/'output/zone-crossings-70959/inventory.json').read_bytes()
    inventory=json.loads(raw)
    audit=json.loads((ROOT/'tools/data/crossing-approaches-manifest.json').read_text())
    verify_inventory(raw,audit)
    edges={e['id']:e for e in inventory['crossings']};maps=inventory['maps']
    def position(p):return f"{maps[str(p['mapID'])]['name']} {p['x']*100:.2f}, {p['y']*100:.2f}"
    def evidence(side):
        via=side.get('viaCrossing')
        return f"dry via link {via['id']}" if via else side['status']
    lines=['# Bridge and zone-crossing live acceptance','',
        'Geometry comes from source build 70959. In-game verification is pending on WoW Forever client build 71091.','',
        '## Test setup','',
        'Install the Mapperly preview into Interface/AddOns and reload the UI. Enable Smart routing and the on-screen route steps. Set a destination by Alt-right-clicking its map location, or enter its X/Y values in Destinations after selecting that zone map.','',
        'For each row, stand at approach A and navigate to approach B, then repeat B to A. Confirm the route actually visits the listed handoff or bridge. The planner can choose a different valid crossing between those ground probes; arriving at B does not test the listed crossing in that case. Test approach A → handoff A, the specific handoff A → B passage, then handoff B → approach B separately, including the reverse direction. A floor-anchor row needs a live reachable starting point inside that city or cave; the handoff alone is not an approach certificate.','',
        'Verify that the line, arrow and current route step progress through the passage and across the native zone change without an off-route loop. Repeat priority cases with Prefer roads off, then Firm, and with Avoid swimming enabled. That setting may fall back to swimming; rows marked swimming-fallback are not dry-only guarantees.','',
        'On a bridge, also test a destination halfway along the deck, a fresh start on the deck, a small detour/rejoin, pause/resume and a reload. If fresh planning cannot establish your elevation, retry from a bank. An established route should continue providing guidance. Do not use a point beneath the deck as a deck-start test.','',
        'If planning fails, click **Copy report** in the error window and press Ctrl+C (Cmd+C on Mac). For a problem while following a route, use `/mapperly report`. Include the link number and direction when sharing the report.','',
        '## Priority circuit','',
        '- Follow the Dun Algaz road from northern Loch Modan through the tunnels to the Wetlands, then return. Check that the arrow follows each tunnel bend and resumes road guidance outside.',
        '- Walk the northern Stranglethorn road across the chasm bridge into Duskwood, then return south. Check that the arrow follows the deck and continues along the road through the zone change in both directions.',
        '- Westfall ↔ Duskwood covered bridge, Ashenvale ↔ Azshara Southfury bridge, and Duskwood ↔ Redridge bridge.',
        '- Wetlands ↔ Arathi Highlands, Dun Morogh ↔ Loch Modan tunnel, and all three Timbermaw branch pairs.',
        '- Ironforge main entrance and Undercity sewer entrance, starting well inside each capital as well as outdoors.',
        '- One small same-zone bridge in Darkshore, a tilted bridge, a narrow rope bridge, and a custom-zone border such as Redridge ↔ Riverglades.',
        '- A journey through several audited exits; a boat/flight journey with walking at both ends; both Great Lift platforms and both tram directions. Transports must remain transport steps, not walking shortcuts.','',
        '## All retained link tests','',
        '| Link | Approach A | Approach B | Exact handoff A → B | Approach evidence A / B |','| --- | --- | --- | --- | --- |']
    for row in sorted(audit['links'],key=lambda row:(maps[str(row['sides'][0]['mapID'])]['name'],row['id'])):
        edge=edges[row['id']];a,b=row['sides']
        lines.append(f"| {row['id']} | {position(a.get('point',edge['a']))} | {position(b.get('point',edge['b']))} | {position(edge['a'])} → {position(edge['b'])} | {evidence(a)} / {evidence(b)} |")
    reviews=json.loads((ROOT/'tools/data/crossing-handoff-review.json').read_text())
    lines+=['','## Withheld shortcuts needing specific evidence','',
        'These exact old handoffs failed the bounded nearby-ground approach audit. They are withheld, not declared physically impassable. A live route showing how to approach them can justify a new source-backed handoff. These numbers are historical IDs, not current link IDs.','',
        '| Previous link | Zones | Previous handoffs |','| --- | --- | --- |']
    for r in reviews['handoffs']:
        ps=[]
        for key,world in [('a',r['worldA']),('b',r['worldB'])]:
            z=maps[str(r[key])];ps.append(position(dict(mapID=r[key],x=(z['west']-world[0])/z['width'],y=(z['north']-world[1])/z['height'])))
        lines.append(f"| {r['previousID']} | {maps[str(r['a'])]['name']} / {maps[str(r['b'])]['name']} | {' → '.join(ps)} |")
    lines+=['','## Remaining source limits','',
        'The 73-map discovery inventory includes instances, test maps and continents; terrain routing covers 55 UI zone/capital/battleground maps. These counts do not imply eighteen missing ordinary zones. Four native-map WDT limitations and every unsupported candidate remain in `bridges-and-crossings-audit.md` and its machine-readable manifest.','',
        'Ownership borders with no certified exit remain unresolved; ocean, cliff and overlapping-artwork adjacencies never become walking permission by inference. Missing terrain masks require a new source/extraction task before they can be certified. Live acceptance can establish gameplay behaviour but does not substitute for missing collision provenance.','']
    (ROOT/'docs/testing-crossing-acceptance.md').write_text('\n'.join(lines),encoding='utf8')
    print('Generated',len(audit['links']),'link tests and',len(reviews['handoffs']),'withheld handoff checks')
if __name__=='__main__':main()
