"""Build native WMO street preferences without changing terrain permissions.

Pinned proofs are upward collidable triangles using explicit mm_street_02 material.
The supplement binds to the exact original road rows and native terrain hash.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'))
from PIL import Image,ImageDraw
from build_roads import encode_rows
ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def read_zone(path,mapid):
    text=path.read_text(encoding='utf-8-sig')
    match=re.search(r'Z\['+str(mapid)+r'\]=\{(.*?),rows=\{\s*(.*?)\}\}',text,re.S)
    if not match:raise ValueError('Missing base zone')
    meta,rows=match.groups();result={k:json.loads(v)for k,v in re.findall(r'(\w+)=("[^"]*"|-?[\d.eE+-]+)',meta)}
    result['rows']=[json.loads(v)for v in re.findall(r'"[^"\n]*"',rows)]
    return result

def decode(z):
    raw=bytearray(z['w']*z['h'])
    if len(z['rows'])!=z['h']:raise ValueError('Invalid row count')
    for y,row in enumerate(z['rows']):
        for x in range(z['w']):
            n=ALPHABET.index(row[x//6])if x//6<len(row)else 0
            raw[y*z['w']+x]=255 if n&(32>>(x%6))else 0
    return bytes(raw)

def build(source):
    result={}
    if source['version']!=1 or source['build']!=70959:raise ValueError('Unexpected source build')
    for proof in source['zones']:
        mid=proof['mapID'];base=read_zone(ROOT/'Data/Roads.lua',mid);terrain=read_zone(ROOT/'Data/Terrain.lua',mid)
        raw=decode(base)
        if hashlib.sha256(raw).hexdigest()!=proof['baseMaskSha256']:raise ValueError('Base road mask changed')
        if terrain['maskSha256']!=proof['terrainMaskSha256']:raise ValueError('Terrain mask changed')
        for k in ('w','h','widthYards','heightYards'):
            if base[k]!=terrain[k]:raise ValueError('Misaligned grids')
        if proof.get('transformProof',{}).get('boundsMaximumError',0)>.01:raise ValueError('Unverified native transform')
        z=proof['bounds'];w,h=base['w'],base['h'];scale=4;im=Image.new('L',(w*scale,h*scale));draw=ImageDraw.Draw(im)
        dock=proof.get('staticDockFloor',{});dockFaces=dock.get('triangles',[])
        if dockFaces and (dock['transformProof']['boundsMaximumError']>.01 or dock['unsupportedSamples'] or dock['minimumHeadroom']<2.2 or dock['maximumPortalStep']>.001):raise ValueError('Unverified dock access floor')
        assets=proof.get('nativeDockFloors',[]);otherDockFaces=[];otherDockKeys=set()
        for asset in assets:
            ap=asset['transformProof']
            if asset['kind']!='native-static-dock-floor' or ap['boundsMaximumError']>.01:raise ValueError('Invalid static dock transform')
            for g in asset['groups']:otherDockKeys.add((ap['root'],ap['placement'],g['fdid']))
            otherDockFaces.extend(asset['triangles'])
        dockFaces=dockFaces+otherDockFaces
        if not proof['triangles']and not dockFaces:raise ValueError('Missing floor witnesses')
        groups={g['fdid']for g in proof['groups']+dock.get('groups',[])+[g for a in assets for g in a['groups']]}
        terrainRaw=decode(terrain)
        for f in proof['triangles']+dockFaces:
            flags=f['flags'];v=f['v']
            if not(flags&8 or flags&32 and not flags&4)or f['group']not in groups :raise ValueError('Invalid floor provenance')
            if f.get('surfaceKind')=='native-static-pier-floor':
                if f['root']!=219576 or f['placement']!=66886228 or f['group']!=219577 or not all(4<p[2]<7 for p in v):raise ValueError('Invalid static dock floor')
            elif f.get('surfaceKind')=='native-static-dock-floor':
                if (f['root'],f['placement'],f['group'])not in otherDockKeys or not f['verticesOriginallyPermitted']:raise ValueError('Invalid static dock provenance')
                for p in v:
                    if math.dist(p[:2],f['nearVesselPosition'][:2])>100.000001:raise ValueError('Dock floor outside native stop bound')
                    x=(z['west']-p[1])/(z['west']-z['east']);y=(z['north']-p[0])/(z['north']-z['south'])
                    if not(0<=x<=1 and 0<=y<=1)or not terrainRaw[min(h-1,int(y*h))*w+min(w-1,int(x*w))]:raise ValueError('Dock vertex outside original terrain permissions')
            elif f['texture']!=proof['textureFileDataID'] or f['root']!=proof['transformProof']['root'] or f['placement']!=proof['transformProof']['placement']:raise ValueError('Invalid street provenance')
            u=[v[1][i]-v[0][i]for i in range(3)];q=[v[2][i]-v[0][i]for i in range(3)];n=[u[1]*q[2]-u[2]*q[1],u[2]*q[0]-u[0]*q[2],u[0]*q[1]-u[1]*q[0]]
            if n[2]<=0 or math.degrees(math.atan2(math.hypot(n[0],n[1]),n[2]))>50.00001:raise ValueError('Invalid upward floor')
            if not all(math.isfinite(x)for p in v for x in p):raise ValueError('Invalid native point')
            draw.polygon([((z['west']-p[1])/(z['west']-z['east'])*w*scale,(z['north']-p[0])/(z['north']-z['south'])*h*scale)for p in v],fill=255)
        added=im.resize((w,h),Image.Resampling.BOX).point(lambda v:255 if v>=64 else 0).tobytes();merged=bytes(max(a,b)for a,b in zip(raw,added))
        result[mid]={**{k:base[k]for k in ('name','w','h','widthYards','heightYards')},'status':'native-street-supplement','terrainMaskSha256':proof['terrainMaskSha256'],'baseMaskSha256':proof['baseMaskSha256'],'baseRoadCells':raw.count(255),'baseRows':base['rows'],'roadCells':merged.count(255),'nativeWMOCells':added.count(255),'addedCells':merged.count(255)-raw.count(255),'maskSha256':hashlib.sha256(merged).hexdigest(),'rows':encode_rows(merged,w,h),'nativeTriangles':len(proof['triangles'])+len(dockFaces),'nativeStreetTriangles':len(proof['triangles']),'nativeDockTriangles':len(dockFaces),'nativeRoot':proof.get('transformProof',assets[0]['transformProof']if assets else {})['root'],'nativePlacement':proof.get('transformProof',assets[0]['transformProof']if assets else {})['placement'],'nativeRoots':sorted({f['root']for f in proof['triangles']+dockFaces}),'nativeSource':'Native WMO street/static dock floor preferences; no terrain permission or boarding transition implied'}
    return result

def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in value.items())+'}'
    if isinstance(value,list):return '{'+','.join(lua(v)for v in value)+'}'
    return json.dumps(value)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'Data/RoadsSupplement.lua');args=parser.parse_args()
    path=ROOT/'tools/data/native-road-supplements-70959.json';source=json.loads(path.read_text());zones=build(source)
    data={'version':1,'build':70959,'proofSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zones':zones}
    args.output.write_text('-- Native WMO street preference supplement; see RoadsSupplement-SOURCES.md.\nlocal _,A=...\nA.RoadSupplementData='+lua(data)+'\n',encoding='utf8')
    for mid,z in zones.items():print(mid,z['baseRoadCells'],'base +',z['addedCells'],'native WMO cells =',z['roadCells'])
if __name__=='__main__':main()
