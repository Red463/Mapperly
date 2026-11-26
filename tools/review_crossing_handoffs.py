"""Re-evaluate alternatives after withholding exact unsupported ground handoffs."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    review_path=ROOT/'tools/data/crossing-handoff-review.json'
    for round in range(64):
        inventory_path=ROOT.parent/'output/zone-crossings-70959/inventory.json'
        inventory=json.loads(inventory_path.read_text())
        audit=json.loads((ROOT/'tools/data/crossing-approaches-manifest.json').read_text())
        edges={e['id']:e for e in inventory['crossings']}
        bad=[row for row in audit['links']if any(s['status']=='unresolved-approach'for s in row['sides'])]
        if not bad:
            print('All selected handoffs have approach evidence; alternatives exhausted or supported.',flush=True);return
        if any(row['structure']for row in bad):raise ValueError('A structure approach needs floor-specific investigation')
        review=json.loads(review_path.read_text());known={json.dumps([r[k]for k in ('a','b','worldA','worldB')])for r in review['handoffs']}
        for row in bad:
            edge=edges[row['id']];ps=[edge[k]for k in ('a','b')];zs=[inventory['maps'][str(p['mapID'])]for p in ps]
            worlds=[[z['west']-p['x']*z['width'],z['north']-p['y']*z['height']]for p,z in zip(ps,zs)]
            record=dict(a=ps[0]['mapID'],b=ps[1]['mapID'],worldA=worlds[0],worldB=worlds[1],
                status='withheld-unproven-approach',previousID=edge['id'],inventorySha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
                approachEvidence=row['sides'])
            key=json.dumps([record[k]for k in ('a','b','worldA','worldB')])
            if key in known:raise ValueError('Withheld handoff resurfaced')
            known.add(key);review['handoffs'].append(record)
        review.setdefault('sourceHashes',{}).update(audit['sourceHashes'])
        review_path.write_text(json.dumps(review,indent=2)+'\n')
        print('Review round',round+1,'withheld',len(bad),'total',len(review['handoffs']),flush=True)
        for script in ('build_crossings.py','audit_crossing_approaches.py'):
            result=subprocess.run([sys.executable,str(ROOT/'tools'/script)],cwd=ROOT,capture_output=True,text=True)
            if result.returncode:raise RuntimeError(result.stdout+'\n'+result.stderr)
    raise RuntimeError('Alternative search has not converged; no completion claim is valid')
if __name__=='__main__':main()
