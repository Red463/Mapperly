"""Extract native road texture layers. Snapshot is read-only; artifacts stay local.

Requires Pillow in .test-deps. Texture names come from wowdev/wow-listfile.
No generic dirt classification, manual tracing or AI-generated geographic data.
"""
from pathlib import Path
import argparse,csv,hashlib,io,json,math,re,struct,sys,urllib.request,zlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'))
sys.path.insert(0,str(ROOT/'tools/roads'))
from PIL import Image,ImageChops
from local_casc import LocalCasc
TILE=1600/3;CELL=TILE/128;ORIGIN=32*TILE
ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
LISTFILE='https://github.com/wowdev/wow-listfile/releases/download/202611211242/community-listfile.csv'

def chunks(blob,start=0,end=None):
    end=len(blob) if end is None else end
    while start<end:
        if start+8>end:raise ValueError('Truncated chunk')
        tag,size=struct.unpack_from('<4sI',blob,start);stop=start+8+size
        if stop>end:raise ValueError('Chunk overflow')
        yield tag[::-1].decode('ascii'),start+8,stop
        start=stop

def road_texture(name):
    return bool(name and ('road' in name.lower() or 'cobblestone' in name.lower()))

def decode_alpha(blob,offset,flags):
    if not flags&512:
        data=blob[offset:]
        if len(data)==2048:
            result=bytes(n for v in data for n in ((v&15)*17,(v>>4)*17))
        else:result=data[:4096]
    else:
        result=bytearray();p=offset
        while len(result)<4096:
            if p>=len(blob):raise ValueError('Truncated alpha')
            control=blob[p];p+=1;n=control&127
            if not n:raise ValueError('Zero alpha run')
            count=1 if control&128 else n
            if p+count>len(blob):raise ValueError('Truncated alpha run')
            result.extend([blob[p]]*n if control&128 else blob[p:p+n]);p+=count
    if len(result)!=4096:raise ValueError('Invalid alpha length')
    return bytes(result)

def tile_roads(blob,names):
    ids=[];index=0;unknown=set();tile=Image.new('L',(1024,1024))
    for tag,a,b in chunks(blob):
        if tag=='MDID':ids=list(struct.unpack('<'+'I'*((b-a)//4),blob[a:b]))
        if tag!='MCNK':continue
        layers=[];cal=b''
        for child,p,q in chunks(blob,a,b):
            if child=='MCLY':layers=[struct.unpack_from('<4I',blob,i) for i in range(p,q,16)]
            elif child=='MCAL':cal=blob[p:q]
        mask=Image.new('L',(64,64))
        for layer,(tex,flags,offset,effect) in enumerate(layers):
            fdid=ids[tex];name=names.get(fdid)
            if not name:unknown.add(fdid)
            limit=layers[layer+1][2] if layer+1<len(layers) else len(cal)
            am=Image.new('L',(64,64),255) if layer==0 else Image.frombytes('L',(64,64),decode_alpha(cal[offset:limit],0,flags))
            mask=ImageChops.multiply(mask,ImageChops.invert(am))
            if road_texture(name):mask=ImageChops.add(mask,am)
        tile.paste(mask,((index%16)*64,(index//16)*64));index+=1
    if index!=256:raise ValueError(f'Expected 256 chunks, got {index}')
    # Mean coverage in a terrain cell, not a single stray road texel.
    return tile.resize((128,128),Image.Resampling.BOX).tobytes(),unknown

def encode_rows(raw,w,h):
    rows=[]
    for y in range(h):
        bits=raw[y*w:(y+1)*w];row=[]
        for x in range(0,w,6):
            n=0
            for i in range(6):n=n*2+int(x+i<w and bits[x+i]>=64)
            row.append(ALPHABET[n])
        rows.append(''.join(row).rstrip('A'))
    return rows

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot-root',type=Path,default=ROOT.parent/'output/forever-datamine-70959')
    parser.add_argument('--artifacts',type=Path,default=ROOT.parent/'output/road-overlays-70959')
    parser.add_argument('--output',type=Path,default=ROOT/'Data/Roads.lua')
    args=parser.parse_args();source=args.snapshot_root.resolve();out=args.artifacts.resolve()
    if out.is_relative_to(source) or args.output.resolve().is_relative_to(source):raise ValueError('Snapshot must stay read-only')
    out.mkdir(parents=True,exist_ok=True);cache=out/'tile-cache';cache.mkdir(exist_ok=True)
    casc=LocalCasc(source);zones=json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']
    wdts={};jobs=[];allids=set();missing=[]
    for z in zones:
        if z['type'] not in (3,6) or 'wdt' not in z:continue
        try:
            if z['wdt'] not in wdts:wdts[z['wdt']]=next(casc.read_fdid(z['wdt'])[a:b] for tag,a,b in chunks(casc.read_fdid(z['wdt'])) if tag=='MAID')
            maid=wdts[z['wdt']];tiles=[]
            tx0,tx1=math.floor((ORIGIN-z['west'])/TILE),math.floor((ORIGIN-z['east'])/TILE)
            ty0,ty1=math.floor((ORIGIN-z['north'])/TILE),math.floor((ORIGIN-z['south'])/TILE)
            if not(0<=tx0<=tx1<64 and 0<=ty0<=ty1<64):raise ValueError('Bounds outside terrain')
            for y in range(ty0,ty1+1):
                for x in range(tx0,tx1+1):
                    at=(y*64+x)*32+12;fdid=int.from_bytes(maid[at:at+4],'little');tiles.append((x,y,fdid))
                    if fdid:
                        try:
                            b=casc.read_fdid(fdid)
                            for tag,p,q in chunks(b):
                                if tag=='MDID':allids.update(struct.unpack('<'+'I'*((q-p)//4),b[p:q]));break
                        except (ValueError,FileNotFoundError,NotImplementedError):pass
            jobs.append((z,tiles,tx0,ty0,tx1,ty1))
        except (ValueError,FileNotFoundError,StopIteration,NotImplementedError) as e:missing.append(dict(id=z['id'],name=z['name'],status='unavailable',reason=str(e)))
    print('Indexed',len(jobs),'zones;',len(allids),'textures',flush=True)
    namepath=out/'texture-names.json'
    names={int(k):v for k,v in json.loads(namepath.read_text()).items()} if namepath.exists() else {}
    wanted=allids-names.keys()
    if wanted:
        with urllib.request.urlopen(LISTFILE,timeout=120) as response:
            for line in response:
                number,sep,path=line.decode('utf-8-sig').strip().partition(';')
                if not sep or not number.isdigit():continue
                fdid=int(number)
                if fdid in wanted:names[fdid]=path
                if fdid>max(wanted):break
        namepath.write_text(json.dumps(names,indent=2),encoding='utf8')
    rows_by_zone={};inventory=list(missing)
    # Native map art for local visual inspection only; it is not packaged.
    db=source/'terrain-research/ashenvale/raw/dbfilesclient'
    def table(name):return list(csv.DictReader((db/(name+'.csv')).open(encoding='utf-8-sig')))
    artmap={int(r['UiMapID']):int(r['UiMapArtID']) for r in table('uimapxmapart')}
    styles={int(r['ID']):r['UiMapArtStyleID'] for r in table('uimapart')}
    layers={r['UiMapArtStyleID']:r for r in reversed(table('uimapartstylelayer')) if r['LayerIndex']=='0'}
    arttiles=table('uimaparttile');reveal=(ROOT/'Data/MapReveal.lua').read_text()
    def map_image(mapid):
        art=artmap[mapid];layer=layers[styles[art]]
        im=Image.new('RGBA',(int(layer['LayerWidth']),int(layer['LayerHeight'])))
        for r in arttiles:
            if int(r['UiMapArtID'])==art and r['LayerIndex']=='0':
                tile=Image.open(io.BytesIO(casc.read_fdid(int(r['FileDataID'])))).convert('RGBA')
                im.alpha_composite(tile,(int(r['ColIndex'])*int(layer['TileWidth']),int(r['RowIndex'])*int(layer['TileHeight'])))
        line=next((s for s in reveal.splitlines() if f'[{art}] =' in s),'')
        for key,value in sorted(re.findall(r'\["([\d:]+)"\] = "([\d, ]+)"',line)):
            w,h,x,y=map(int,key.split(':'));cols=math.ceil(w/256)
            for i,fdid in enumerate(map(int,re.findall(r'\d+',value))):
                col,row=i%cols,i//cols
                tile=Image.open(io.BytesIO(casc.read_fdid(fdid))).convert('RGBA').crop((0,0,min(256,w-col*256),min(256,h-row*256)))
                im.alpha_composite(tile,(x+col*256,y+row*256))
        return im
    for z,tiles,tx0,ty0,tx1,ty1 in jobs:
        mosaic=Image.new('L',((tx1-tx0+1)*128,(ty1-ty0+1)*128));bad=[];unknown=set();decoded=0
        for x,y,fdid in tiles:
            try:
                if not fdid:raise FileNotFoundError('No texture tile')
                path=cache/f'{fdid}.zlib'
                if path.exists():
                    payload=json.loads(zlib.decompress(path.read_bytes()));raw=bytes.fromhex(payload['mask']);u=payload['unknown']
                else:
                    raw,u=tile_roads(casc.read_fdid(fdid),names)
                    path.write_bytes(zlib.compress(json.dumps(dict(mask=raw.hex(),unknown=sorted(u))).encode()))
                unknown.update(u);mosaic.paste(Image.frombytes('L',(128,128),raw),((x-tx0)*128,(y-ty0)*128));decoded+=1
            except (ValueError,FileNotFoundError,IndexError,NotImplementedError) as e:bad.append([x,y,str(e)])
        w,h=math.ceil((z['west']-z['east'])/CELL),math.ceil((z['north']-z['south'])/CELL)
        crop=((ORIGIN-z['west'])/CELL-tx0*128,(ORIGIN-z['north'])/CELL-ty0*128,(ORIGIN-z['east'])/CELL-tx0*128,(ORIGIN-z['south'])/CELL-ty0*128)
        mask=mosaic.transform((w,h),Image.Transform.EXTENT,crop,Image.Resampling.NEAREST)
        mask=mask.point(lambda v:255 if v>=64 else 0);raw=mask.tobytes();mask.save(out/f'{z["id"]}-mask.png')
        status='unavailable' if not decoded else 'partial' if bad or unknown else 'complete'
        record=dict(id=z['id'],name=z['name'],status=status,w=w,h=h,widthYards=z['west']-z['east'],heightYards=z['north']-z['south'],roadCells=raw.count(255),decodedTiles=decoded,missingTiles=bad,unknownTextures=sorted(unknown),maskSha256=hashlib.sha256(raw).hexdigest())
        if decoded:rows_by_zone[z['id']]=(record,encode_rows(raw,w,h))
        try:
            base=map_image(z['id']);overlay=Image.new('RGBA',base.size,(45,230,255));overlay.putalpha(mask.resize(base.size,Image.Resampling.LANCZOS).point(lambda v:round(v*.9)))
            overlay.save(out/f'{z["id"]}-transparent.png');Image.alpha_composite(base,overlay).save(out/f'{z["id"]}-overlay.png');record['overlay']=True
        except (KeyError,ValueError,FileNotFoundError,NotImplementedError) as e:record['artError']=str(e)
        inventory.append(record);print(z['id'],z['name'],status,record['roadCells'],'road cells',flush=True)
    lines=['-- Generated native road/cobblestone coverage, build 70959. See Roads-SOURCES.md.','local _,A=...','A.RoadData={version=1,build=70959,zones={}}','local Z=A.RoadData.zones']
    for id,(r,rows) in sorted(rows_by_zone.items()):
        lines.append(f'Z[{id}]={{'+','.join(k+'='+json.dumps(r[k]) for k in ['name','status','w','h','widthYards','heightYards','roadCells'])+',rows={')
        lines.extend(json.dumps(s)+',' for s in rows);lines.append('}}')
    args.output.write_text('\n'.join(lines)+'\n',encoding='utf8')
    report=dict(build=70959,method='Effective road/cobblestone alpha coverage, mean >=25% in ~4.17-yard terrain cells. Generic dirt excluded.',listfile=LISTFILE,zones=inventory)
    (out/'inventory.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    import html
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Mapperly roads</title><style>body{background:#171b20;color:white;font:16px sans-serif}section{display:inline-block;width:48%;vertical-align:top}img{max-width:100%}</style><h1>Native road overlays: build 70959</h1><p>Cyan: road/cobblestone terrain texture. Paving included; dirt excluded. Gaps are not blocked terrain.</p>'+''.join(f'<section><h2>{r["id"]} {html.escape(r["name"])}</h2><p>{r["status"]}; {r.get("roadCells",0)} road cells</p>'+ (f'<a href="{r["id"]}-overlay.png"><img loading="lazy" src="{r["id"]}-overlay.png"></a>' if r.get('overlay') else '<p>Map artwork unavailable; see mask PNG.</p>')+'</section>' for r in inventory),encoding='utf8')
    print('DONE',len(rows_by_zone),'masks',args.output.stat().st_size,'bytes',flush=True)

if __name__=='__main__':main()
