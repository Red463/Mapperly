"""Readable timing/failure report for benchmark_route_matrix.py outputs."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,statistics
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/route-matrix-2026-11-25'

def main():
    matrix=json.loads((OUT/'matrix.json').read_text());cases={c['id']:c for c in matrix['cases']}
    for f,sha in matrix['sourceHashes'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=sha:raise ValueError('Benchmark source changed: '+f)
    rows=[]
    for file in sorted(OUT.glob('*.jsonl')):
        if file.stem=='pilot':continue
        for line in file.read_text().splitlines():
            if line.strip():rows.append(dict(json.loads(line),batch=file.stem))
    fields=['batch','case','category','from','to','profile','temperature','flights','avoidSwimming','walkingOnly','status','hostSeconds','modeled60fpsSeconds','slices','maxStepMS','paths','cells','bakedHits','cacheHits','actualZones','vehicles','reason']
    flat=[]
    for r in rows:
        c=cases[r['case']];p=r.get('progress',{})
        flat.append(dict(**{k:r.get(k,'')for k in fields if k in r and k not in ('actualZones','vehicles')},category=c['category'],**{'from':c['start']['name'],'to':c['goal']['name']},
            paths=p.get('paths'),cells=p.get('cells'),bakedHits=r.get('pathReuseDelta',{}).get('bakedHits'),cacheHits=r.get('pathReuseDelta',{}).get('hits'),
            actualZones=' > '.join(str(x)for x in r.get('actualZones',[])),vehicles=' / '.join(v['kind']+':'+v['name']for v in r.get('vehicles',[]))))
    with (OUT/'route-timings.csv').open('w',newline='',encoding='utf8')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(flat)
    failures=[r for r in rows if r['status']!='ok'];primary=[r for r in rows if r['batch']=='primary']
    text=['# Mapperly route-generation survey — 25 November 2026','',
        f"**{len(cases)} distinct routes; {len(rows)} completed measurement records; {sum(r['status']=='ok'for r in rows)} successes; {len(failures)} failures/timeouts/harness errors.** Counts include cold and immediate-repeat runs and all configurations; they are not distinct destinations.",'',
        f"Primary survey: {len({r['case']for r in primary})} routes measured so far; {len({(r['case'],r['profile'])for r in primary if r['status']!='ok'})} failing route/road-mode combinations across {len({r['case']for r in primary if r['status']!='ok'})} distinct routes.",'',
        '## Method and limits','',
        '- Production Lua 5.1 planner and all current terrain, water, roads, structures, docks, transports, trams and shipped walking paths. No routing algorithm or permission changes were made.',
        '- Cold = fresh Lua runtime with shipped precomputed paths but no session history. Warm = immediate identical retry in that runtime. Setup and post-plan geometry validation are outside the route timer.',
        '- Tables report measured host computation elapsed seconds. These are **not live in-game timings**. Benchmarks run sequentially, so separate route tests do not compete for CPU.',
        '- `modeled60fpsSeconds` is a scheduling estimate only: one actual PlanningJob.Step per hypothetical 60fps frame, using a real monotonic host clock for the four-millisecond slice budget. It excludes game load, UI rendering and hardware differences. It is not a measurement or promise of game latency.',
        '- Zone count includes start and destination: two zones means one border. Categories use the minimum supported walking-graph chain; the actual selected route can cross different/more zones or use a transport. Controlled walking-only rows exclude transports; primary rows retain normal transport choices.',
        '- Primary characters have no recorded flight offers. Targeted flight runs use an explicitly synthetic recorded character with native same-faction segment chains between selected hubs. This does not test or assume the user’s own flight knowledge.',
        '- Coordinates are retained in matrix.json. Named town anchors move at most 60 yards to permitted ground when needed; all movement is recorded. A permitted cell is not proof of physical reachability or safety from hostile NPCs.',
        '- Avoid swimming is off unless flagged. Road keys: light=1, moderate=2, normal=Balanced (3), firm=4, strong=5; Off disables road preference. Other strengths and swimming comparisons are labelled separately.',
        '- A 45-second per-plan host safety limit cancels the benchmark (timeout ≠ proven no route). Budget errors are the planner’s actual failures. Failed repeated attempts remain recorded. Native-floor guidance and Ironforge wayfinding are not live collision certificates.','',
        '## Primary cold timing by minimum walking zone count','',
        '| Zones | Road mode | Attempts | Success | Failed | Median host s | Worst host s |','| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    user=[r for r in rows if r['batch']in('user-route','user-route-light-moderate')]
    if user:
        section=['## Reported route: Ratchet → Shimmering Flats','',
            'Swimming is permitted. Coordinates are inferred town-area points: Ratchet 62.4, 37.8; Thousand Needles 78.0, 75.0. No user flight-knowledge snapshot was supplied. These runs use the normal transport settings without recorded flight offers.','',
            '| Roads | Cold host s | Repeat host s | Cold 60fps model s | Cold result | Repeat result | Cold vehicle |','| --- | ---: | ---: | ---: | --- | --- | --- |']
        for profile in ('off','light','moderate','normal','firm','strong'):
            cold=next((r for r in user if r['profile']==profile and r.get('temperature')=='cold'),None)
            warm=next((r for r in user if r['profile']==profile and r.get('temperature')=='warm'),None)
            if cold:section.append(f"| {'Balanced'if profile=='normal'else profile} | {cold['hostSeconds']:.3f} | {warm['hostSeconds']if warm else '—'} | {cold['modeled60fpsSeconds']:.3f} | {cold['status']} | {warm['status']if warm else '—'} | {'; '.join(v['kind']+': '+v['name']for v in cold.get('vehicles',[]))or '—'} |")
        section+=['','']
        at=text.index('## Primary cold timing by minimum walking zone count');text[at:at]=section
    order=['1','2','3','4','5','6','7','8+','cross-continent']
    for group in order:
        for profile in ('off','firm'):
            rs=[r for r in primary if cases[r['case']]['category']==group and r['profile']==profile and r.get('temperature')=='cold']
            if not rs:continue
            times=[r['hostSeconds']for r in rs if 'hostSeconds'in r]
            text.append(f"| {group} | {profile} | {len(rs)} | {sum(r['status']=='ok'for r in rs)} | {sum(r['status']!='ok'for r in rs)} | {statistics.median(times):.3f} | {max(times):.3f} |")
    text+=['','## Every primary route','',
        'Seconds below are measured host computation. `FAIL` and `TIMEOUT` retain elapsed time; a fast failure does not count as a fast usable route.','',
        '| ID | Zones | Route | Off cold / warm s | Firm cold / warm s |','| --- | --- | --- | --- | --- |']
    def timing(r):return ('—'if r is None else f"{r.get('hostSeconds',0):.3f}"+(' '+r['status'].upper()if r['status']!='ok'else''))
    for c in cases.values():
        if not any(r['case']==c['id']for r in primary):continue
        values=[]
        for profile in ('off','firm'):
            values.append(' / '.join(timing(next((r for r in primary if r['case']==c['id']and r['profile']==profile and r.get('temperature')==t),None))for t in ('cold','warm')))
        text.append(f"| {c['id']} | {c['category']} | {c['start']['name']} → {c['goal']['name']} | {values[0]} | {values[1]} |")
    text+=['','## Supplementary controlled tests','',
        '| Batch | ID | Route | Roads | Flights | Dry-first | Walking only | Cold/warm | Host s | 60fps model s | Status |','| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |']
    for r in rows:
        if r['batch']=='primary':continue
        c=cases[r['case']];text.append(f"| {r['batch']} | {r['case']} | {c['start']['name']} → {c['goal']['name']} | {r['profile']} | {r.get('flights',False)} | {r.get('avoidSwimming',False)} | {r.get('walkingOnly',False)} | {r.get('temperature','—')} | {r.get('hostSeconds',0):.3f} | {r.get('modeled60fpsSeconds',0):.3f} | {r['status']} |")
    text+=['','## Cross-continent itineraries','',
        '| ID | Roads | Status | Host cold s | Zones actually walked | Vehicles selected |','| --- | --- | --- | ---: | --- | --- |']
    names={a['point']['mapID']:a['zone']for a in matrix['anchors'].values()}
    for r in primary:
        if cases[r['case']]['category']!='cross-continent'or r.get('temperature')!='cold':continue
        zones=' → '.join(names.get(id,str(id))for id in r.get('actualZones',[]))
        vehicles='; '.join(v['kind']+': '+v['name']for v in r.get('vehicles',[]))
        text.append(f"| {r['case']} | {r['profile']} | {r['status']} | {r.get('hostSeconds',0):.3f} | {zones or '—'} | {vehicles or '—'} |")
    anomalies=[]
    for r in primary:
        if r.get('temperature')!='cold':continue
        ids=[v['id']for v in r.get('vehicles',[])if v['kind']=='tram']
        if 'tram:deeprun:1453:1455'in ids and 'tram:deeprun:1455:1453'in ids:anomalies.append(r)
    if anomalies:
        text+=['','## Itinerary anomalies requiring review','',
            'These plans completed and passed their applicable terrain checks, but have a questionable travel sequence. This is separate from a generation failure and does not establish global travel-time optimality.','',
            '| ID | Route | Roads | Observed sequence |','| --- | --- | --- | --- |']
        for r in anomalies:
            c=cases[r['case']];text.append(f"| {r['case']} | {c['start']['name']} → {c['goal']['name']} | {r['profile']} | Stormwind → Ironforge → Stormwind by tram, then onward. Investigate whether a direct city/harbour approach should avoid this return trip. |")
    text+=['','## Primary failures by route','',
        'A budget failure is not proof that no physical route exists. It means this attempt did not find a complete usable itinerary within the planner’s work allowance.','',
        '| ID | Route | Failing cold road modes | Cold host s | Immediate retry |','| --- | --- | --- | --- | --- |']
    for id in cases:
        bad=[r for r in primary if r['case']==id and r.get('temperature')=='cold'and r['status']!='ok']
        if not bad:continue
        c=cases[id];retries=[r for r in primary if r['case']==id and r.get('temperature')=='warm'and r['profile']in{r['profile']for r in bad}]
        text.append(f"| {id} | {c['start']['name']} → {c['goal']['name']} | {', '.join(r['profile']for r in bad)} | {', '.join(str(r.get('hostSeconds','—'))for r in bad)} | {'; '.join(r['profile']+': '+r['status']+' '+str(r.get('hostSeconds','—'))+'s'for r in retries)} |")
    text+=['','## Failure inventory','',
        '| Batch | ID | Roads | Cold/warm | Host s | Paths | Cells | Result |','| --- | --- | --- | --- | ---: | ---: | ---: | --- |']
    for r in failures:
        p=r.get('progress',{});text.append(f"| {r['batch']} | {r['case']} | {r['profile']} | {r.get('temperature','—')} | {r.get('hostSeconds',0):.3f} | {p.get('paths','—')} | {p.get('cells','—')} | {r['status']}: {r.get('reason')or r.get('invalidWalkingLegs')} |")
    text+=['','## Slowest cold computations','',
        '| Batch | ID | Roads | Host s | 60fps model s | Paths | Cells | Max step ms | Status |','| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in sorted((r for r in rows if r.get('temperature')=='cold'),key=lambda r:r.get('hostSeconds',0),reverse=True)[:15]:
        p=r.get('progress',{});text.append(f"| {r['batch']} | {r['case']} | {r['profile']} | {r.get('hostSeconds',0):.3f} | {r.get('modeled60fpsSeconds',0):.3f} | {p.get('paths','—')} | {p.get('cells','—')} | {r.get('maxStepMS',0):.1f} | {r['status']} |")
    text+=['','## Exact test anchors','',
        '| Place | Map | X | Y | Adjustment yd |','| --- | --- | ---: | ---: | ---: |']
    for name,a in matrix['anchors'].items():
        p=a['point'];text.append(f"| {name} | {a['zone']} ({p['mapID']}) | {p['x']*100:.4f} | {p['y']*100:.4f} | {a['adjustmentYards']:.2f} |")
    text+=['','## Findings and follow-up priorities','',
        'Observed: zone count alone is a poor predictor. Several adjacent-zone plans exhaust their budget, while long journeys with a useful tram, flight or boat can be cheap. A failed budgeted search does not prove that a route is physically impossible.','',
        'Observed: successful route sections benefit strongly from session caching, but budget-limited subsearches can repeat on every request. In the traced Astranaar → Azshara Firm repeat, one failed 262,144-cell search dominates while successful sections cost almost nothing. The adjacent Ashenvale → Darkshore trace invokes 128 local searches across 18 map IDs before failing; attempted maps are not necessarily part of a final journey.','']
    ratchet=next((r for r in user if r['profile']=='off'and r.get('temperature')=='warm'and r.get('trace')),None)
    if ratchet:
        failed=[t for t in ratchet['trace']if t['status']=='budget']
        text+=['For the reported Ratchet → Shimmering Flats route, the repeat with roads off uses the Great Lift but still performs '+str(len(failed))+' budget-limited subsearches ('+str(sum(t['cells']for t in failed))+' cells). The expensive alternatives are in Dustwallow Marsh, although the returned walking legs use the Barrens and Thousand Needles. This directly reproduces the reported delay with swimming permitted.','']
    text+=['Observed: known flight offers can avoid expensive walking sections, but the flight fixture is not a substitute for good walking performance. Dry-first swimming preference can also spend a full unsuccessful pass before retrying with swimming allowed; those results are kept outside the baseline.','',
        'Suggested implementation priorities, not changes made during this survey:','',
        '1. Reuse budget-limited failure results only under the same source signatures, endpoints, road/liquid policy and an equal or smaller search allowance. Do not cache a budget failure as permanent unreachability.',
        '2. Bound or defer expensive alternative walking sections when a complete usable itinerary already exists. In particular, avoid repeatedly spending the full local allowance on low-value Dustwallow alternatives to the Great Lift.',
        '3. Connect arbitrary first/last-mile locations to the prepared road/crossing network, rather than depending only on exact endpoint matches for prepared path reuse. Preserve terrain and native-floor validation.',
        '4. Re-test these exact failure cases before increasing work budgets. A larger ceiling alone risks making failed requests take even longer. Review the tram-return itinerary separately from latency.','']
    text+=['','Reproduce: `python tools/benchmark_route_matrix.py --prepare`, then `--run`. Use `--cases R01,R05 --profiles off,firm --label example` for a subset; add `--walking`, `--flights` or `--avoid` for the labelled controls. Run this report with `python tools/report_route_matrix.py`. Raw JSONL and flattened CSV retain actual chosen zones, vehicles, source hashes, cache hits, search cells and precise coordinates.','']
    path=ROOT/'docs/route-generation-survey-2026-11-25.md';path.write_text('\n'.join(text),encoding='utf8')
    (OUT/'benchmark-results.json').write_text(json.dumps(dict(matrix=matrix,measurements=rows,sourceVerified=True),indent=2)+'\n')
    print('Report',path,'measurements',len(rows),'failures',len(failures),'primary records',len(primary))
if __name__=='__main__':main()
