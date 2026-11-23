from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from build_crossings import select_dry_crossings
samples={(1,2):[((0,0),(4,0)),((10,0),(14,0)),((150,0),(154,0)),((300,0),(304,0)),((450,0),(454,0))],(2,3):[((0,0),(4,0))]}
chosen=select_dry_crossings(samples,{(2,3)},lambda id,p:abs(p[0]-150))
assert len(chosen)==3 and all(row[:2]==(1,2) for row in chosen)
assert chosen[0][2]==(150,0),'validated untextured terrain should prefer a crossing near road approaches'
for i,a in enumerate(chosen):
 for b in chosen[i+1:]:assert __import__('math').dist(a[2],b[2])>=100
print('PASS: dry native-boundary selection is road-independent, ranked, bounded and deduplicated')
