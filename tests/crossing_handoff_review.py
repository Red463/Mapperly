from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from build_crossings import reviewed_handoffs,select_road_crossings
edge=(1,2,(10.,20.),(30.,40.))
rule=dict(a=1,b=2,worldA=[10.,20.],worldB=[30.,40.],status='withheld-unproven-approach')
assert reviewed_handoffs([edge],[rule])==[]
assert reviewed_handoffs([(1,2,(10.,20.),(31.,40.))],[rule])!=[],'a changed verified handoff is not a blanket zone-pair ban'
assert reviewed_handoffs([edge],[dict(rule,status='resolved')])==[edge]
alternative=(1,2,(11.,20.),(31.,40.))
assert select_road_crossings([edge,alternative],[rule])==[alternative], 'withheld handoffs must not suppress a nearby replacement before spacing'
review=json.loads((root/'tools/data/crossing-handoff-review.json').read_text())
assert len(review['handoffs'])>=8
assert all(any(s['status']=='unresolved-approach'for s in row['approachEvidence'])for row in review['handoffs'])
print('PASS: exact unproven handoffs withheld without banning zone pairs or changed landings')
