"""Replay pinned harbour floor vertices/flags directly from read-only native CASC."""
from pathlib import Path
import argparse,hashlib,json,math,struct,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/roads'))
from local_casc import LocalCasc
from build_roads import chunks
from build_structure_corridors import validate_curved

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--snapshot-root',type=Path,default=ROOT.parent/'output/forever-datamine-70959');args=parser.parse_args();c=LocalCasc(args.snapshot_root)
    source=json.loads((ROOT/'tools/data/native-harbour-corridors-70959.json').read_text());zone=next(z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']if z['id']==1453);origin=32*1600/3;tile=1600/3
    wdt=c.read_fdid(zone['wdt']);maid=next(wdt[a:b]for tag,a,b in chunks(wdt)if tag=='MAID');placements={}
    for ty in range(math.floor((origin-zone['north'])/tile),math.floor((origin-zone['south'])/tile)+1):
        for tx in range(math.floor((origin-zone['west'])/tile),math.floor((origin-zone['east'])/tile)+1):
            for fid in struct.unpack_from('<8I',maid,(ty*64+tx)*32)[1:3]:
                if not fid:continue
                raw=c.read_fdid(fid)
                for tag,a,b in chunks(raw):
                    if tag!='MODF':continue
                    for at in range(a,b,64):
                        root,uid=struct.unpack_from('<II',raw,at);pos=struct.unpack_from('<3f',raw,at+8);rot=struct.unpack_from('<3f',raw,at+20);bounds=struct.unpack_from('<6f',raw,at+32);placements[uid]=(root,pos,rot,bounds,fid)
    total=0
    for row in source:
        length=validate_curved(row);root,pos,rot,bounds,placementADT=placements[row['placement']];assert root==row['wmo']and rot[0]==rot[2]==0
        raw=c.read_fdid(root);assert hashlib.sha256(raw).hexdigest()==row['nativeRootSha256'];rc={tag:raw[a:b]for tag,a,b in chunks(raw)};box=struct.unpack_from('<6f',rc['MOHD'],36);ct,st=math.cos(math.radians(rot[1])),math.sin(math.radians(rot[1]))
        def world(v):
            x,y,z=v;return[origin-pos[2]-(ct*x-st*y),origin-pos[0]-(st*x+ct*y),pos[1]+z]
        vv=[(pos[0]+st*x+ct*y,pos[1]+z,pos[2]+ct*x-st*y)for x in(box[0],box[3])for y in(box[1],box[4])for z in(box[2],box[5])];actual=[min(p[k]for p in vv)for k in range(3)]+[max(p[k]for p in vv)for k in range(3)];assert max(abs(a-b)for a,b in zip(actual,bounds))<.01
        metadata={g['fdid']:g for g in row['nativeGroups']};groups={}
        for f in row['faces']:
            fid=f['fdid']
            if fid not in groups:
                raw=c.read_fdid(fid);assert hashlib.sha256(raw).hexdigest()==metadata[fid]['sha256'];a,b=next((a,b)for tag,a,b in chunks(raw)if tag=='MOGP');gc={tag:raw[s:e]for tag,s,e in chunks(raw,a+68,b)};vs=list(struct.iter_unpack('<3f',gc['MOVT']));ix=list(struct.iter_unpack('<3H',gc['MOVI']));polys=list(struct.iter_unpack('<HH',gc['MPY2']))if'MPY2'in gc else list(struct.iter_unpack('<BB',gc['MOPY']));assert len(ix)==len(polys);groups[fid]=(vs,ix,polys)
            vs,ix,polys=groups[fid];flags,material=polys[f['triangle']];assert flags==f['sourceFlags']and(flags&8 or flags&32 and not flags&4);native=[world(vs[k])for k in ix[f['triangle']]];assert max(abs(a-b)for p,q in zip(native,f['v'])for a,b in zip(p,q))<1e-8
            total+=1
        print(row['name']+':',len(row['faces']),'exact native faces,',len(row['samples']),'supported samples,',round(length,3),'horizontal yards; native placement ADT',placementADT)
    print('PASS:',total,'native floor triangle witnesses, placement transforms, original hashes and curved corridor validation')
if __name__=='__main__':main()
