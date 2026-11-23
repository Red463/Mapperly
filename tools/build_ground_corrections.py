"""Restore raw dry ground islands linked by independently audited native floors."""
from pathlib import Path
import sys,json,collections,hashlib,math,zlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'));sys.path.insert(0,str(ROOT/'tools'))
from PIL import Image
from lupa.lua51 import LuaRuntime
from build_roads import LocalCasc,chunks,TILE,CELL,ORIGIN,encode_rows

def main():
    source=ROOT.parent/'output/forever-datamine-70959';out=ROOT.parent/'output/zone-crossings-70959'
    rows=json.loads((out/'structure-corridors.json').read_text());zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
    lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={};assert(loadstring(...))("Mapperly",A)',(ROOT/'Data/Terrain.lua').read_text())
    c=LocalCasc(source);result={};report=[]
    for map in sorted({p['mapID'] for row in rows.values() for p in [row['a'],row['b']]}):
        z=zones[map];base=Image.open(ROOT.parent/f'output/terrain-overlays-70959/{map}.png').convert('L');w,h=base.size
        x0,x1=math.floor((ORIGIN-z['west'])/TILE),math.floor((ORIGIN-z['east'])/TILE)
        y0,y1=math.floor((ORIGIN-z['north'])/TILE),math.floor((ORIGIN-z['south'])/TILE)
        b=c.read_fdid(z['wdt']);maid=next(b[a:e] for tag,a,e in chunks(b) if tag=='MAID');mosaic=Image.new('L',((x1-x0+1)*128,(y1-y0+1)*128),64)
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                fdid=int.from_bytes(maid[(y*64+x)*32:(y*64+x)*32+4],'little');path=ROOT.parent/f'output/terrain-overlays-70959/tile-cache/{fdid}.zlib'
                if path.exists():mosaic.paste(Image.frombytes('L',(128,128),zlib.decompress(path.read_bytes())),((x-x0)*128,(y-y0)*128))
        crop=((ORIGIN-z['west'])/CELL-x0*128,(ORIGIN-z['north'])/CELL-y0*128,(ORIGIN-z['east'])/CELL-x0*128,(ORIGIN-z['south'])/CELL-y0*128)
        raw=mosaic.transform((w,h),Image.Transform.EXTENT,crop,Image.Resampling.NEAREST)
        correction=Image.new('L',(w,h));allAdded=set()
        for row in rows.values():
            for p in [row['a'],row['b']]:
                if p['mapID']!=map:continue
                seed=min(w-1,int(p['x']*w)),min(h-1,int(p['y']*h))
                if base.getpixel(seed) in (128,255) or seed in allAdded:continue
                if raw.getpixel(seed)!=255:raise ValueError('Native landing is not dry permitted root terrain')
                visited={seed};q=collections.deque([seed]);reaches=False
                while q and len(visited)<30000:
                    x,y=q.popleft()
                    if base.getpixel((x,y)) in (128,255):reaches=True
                    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        n=x+dx,y+dy
                        if 0<=n[0]<w and 0<=n[1]<h and n not in visited and raw.getpixel(n)==255:visited.add(n);q.append(n)
                if q or reaches:raise ValueError('Correction is not an enclosed native-ground component')
                for cell in visited:correction.putpixel(cell,255)
                allAdded.update(visited);report.append(dict(mapID=map,structure=row['placement'],cells=len(visited),seed=seed))
        if allAdded:
            correction.save(out/f'{map}-ground-corrections.png')
            result[map]=dict(w=w,h=h,baseSha256=lua.globals().A.TerrainData.zones[map].maskSha256,maskSha256=hashlib.sha256(correction.tobytes()).hexdigest(),cells=len(allAdded),rows=encode_rows(correction.tobytes(),w,h))
    def literal(v):
        if isinstance(v,dict):return '{'+','.join('['+literal(k)+']='+literal(x) for k,x in v.items())+'}'
        if isinstance(v,list):return '{'+','.join(literal(x) for x in v)+'}'
        return json.dumps(v)
    (ROOT/'Data/GroundCorrections.lua').write_text('-- Original dry terrain restored where audited native tunnels connect enclosed valleys.\nlocal _,A=...\nA.GroundCorrectionData='+literal(dict(version=1,build=70959,zones=result))+'\n')
    (out/'ground-corrections.json').write_text(json.dumps(report,indent=2))
    print('Restored native dry cells:',sum(r['cells'] for r in report),report)

if __name__=='__main__':main()
