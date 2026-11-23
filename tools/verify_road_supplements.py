"""Replay pinned street/static-dock preferences against original native CASC facts."""
from pathlib import Path
import argparse,hashlib,json,math,struct,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/roads'))
from local_casc import LocalCasc
from build_roads import chunks
from build_road_supplements import build

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--snapshot-root',type=Path,default=ROOT.parent/'output/forever-datamine-70959');args=parser.parse_args();c=LocalCasc(args.snapshot_root)
    source=json.loads((ROOT/'tools/data/native-road-supplements-70959.json').read_text());origin=32*1600/3;cache={};total=0
    for zone in source['zones']:
        assets=[]
        if zone.get('triangles'):assets.append({'transformProof':zone['transformProof'],'groups':zone['groups'],'triangles':zone['triangles']})
        if zone.get('staticDockFloor'):assets.append(zone['staticDockFloor'])
        assets.extend(zone.get('nativeDockFloors',[]));count=0
        for asset in assets:
            p=asset['transformProof'];root,uid=p['root'],p['placement'];modf=c.read_fdid(p['sourceMODFADT']);placement=None
            for tag,a,b in chunks(modf):
                if tag!='MODF':continue
                for at in range(a,b,64):
                    rr,uu=struct.unpack_from('<II',modf,at)
                    if rr==root and uu==uid:placement=at
            assert placement is not None
            pos=struct.unpack_from('<3f',modf,placement+8);rot=struct.unpack_from('<3f',modf,placement+20);bounds=struct.unpack_from('<6f',modf,placement+32);flags,_,_,scale=struct.unpack_from('<4H',modf,placement+56);scale=scale/1024 if flags&4 else 1
            assert list(pos)==p['position']and list(rot)==p['rotation']and scale==p['scale']and rot[0]==rot[2]==0
            raw=c.read_fdid(root);assert hashlib.sha256(raw).hexdigest()==p['rootSha256'];rc={tag:raw[a:b]for tag,a,b in chunks(raw)};ng=struct.unpack_from('<I',rc['MOHD'],4)[0];gids=set(struct.unpack_from('<'+'I'*ng,rc['GFID'][:ng*4]));box=struct.unpack_from('<6f',rc['MOHD'],36);ct,st=math.cos(math.radians(rot[1])),math.sin(math.radians(rot[1]))
            def world(v):
                x,y,z=v;return[origin-pos[2]-scale*(ct*x-st*y),origin-pos[0]-scale*(st*x+ct*y),pos[1]+scale*z]
            vv=[(pos[0]+scale*(st*x+ct*y),pos[1]+scale*z,pos[2]+scale*(ct*x-st*y))for x in(box[0],box[3])for y in(box[1],box[4])for z in(box[2],box[5])];actual=[min(v[k]for v in vv)for k in range(3)]+[max(v[k]for v in vv)for k in range(3)];assert max(abs(a-b)for a,b in zip(actual,bounds))<.01
            metadata={g['fdid']:g for g in asset['groups']}
            for f in asset['triangles']:
                fid=f['group'];assert fid in gids
                if fid not in cache:
                    blob=c.read_fdid(fid);sha=hashlib.sha256(blob).hexdigest();a,b=next((a,b)for tag,a,b in chunks(blob)if tag=='MOGP');gc={tag:blob[s:e]for tag,s,e in chunks(blob,a+68,b)};vs=list(struct.iter_unpack('<3f',gc['MOVT']));ix=list(struct.iter_unpack('<3H',gc['MOVI']));polys=list(struct.iter_unpack('<HH',gc['MPY2']))if'MPY2'in gc else list(struct.iter_unpack('<BB',gc['MOPY']));assert len(ix)==len(polys);cache[fid]=(sha,vs,ix,polys)
                sha,vs,ix,polys=cache[fid];assert sha==metadata[fid]['sha256'];ff,material=polys[f['triangle']];assert ff==f['flags']and material==f['material']and(ff&8 or ff&32 and not ff&4);native=[world(vs[k])for k in ix[f['triangle']]];assert max(abs(a-b)for v,w in zip(native,f['v'])for a,b in zip(v,w))<1e-8
                if not f.get('surfaceKind'):assert struct.unpack_from('<I',rc['MOMT'],material*64+12)[0]==127976
                count+=1
        print(zone['mapID'],count,'exact native floor triangles');total+=count
    build(source)
    print('PASS:',total,'native triangles; original hashes, flags, materials, placements, transforms, base masks and static dock distance/permission bounds')
if __name__=='__main__':main()
