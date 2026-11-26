"""Validate pinned native WMO floor proofs; emit narrowly scoped walking corridors."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]

def validate(row):
    points=row['worldCenterline']
    if not row['nativeFloorSupported'] or row['unsupportedInteriorSamples'] or len(points)<3:raise ValueError('Missing native floor support')
    if row['minimumCenterlineHeadroom']<2 or row['maxAdjacentFloorRise']>.3 or row['maxAdjacentFloorDrop']<-.3:raise ValueError('Unsupported floor profile')
    if not all(x['terrain']['permitted'] and not x['terrain']['hole'] and not x['terrain']['liquid'] for x in row['terrainLandings']):raise ValueError('Invalid outdoor landing')
    a,b=points[0],points[-1];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    if not 1<length<300:raise ValueError('Unexpected structure span')
    previous=-1
    for p in points:
        t=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(length*length)
        cross=abs((p[0]-a[0])*dy-(p[1]-a[1])*dx)/length
        if not all(math.isfinite(n) for n in p) or cross>.001 or t<previous-1e-8 or not -1e-8<=t<=1.00000001:raise ValueError('Nonlinear or discontinuous corridor')
        previous=t
    for p,q in zip(points,points[1:]):
        if math.dist(p[:2],q[:2])>.51 or abs(p[2]-q[2])>.55:raise ValueError('Unsampled gap or excessive step')
    return a,b,length

def validate_curved(row):
    limit=.3
    if 'kerbSteps' in row:
        points=row['worldCenterline']
        steps=[abs(a[2]-b[2]) for a,b in zip(points,points[1:])]
        joints=[i for i,rise in enumerate(steps,1) if rise>.3]
        if (row['placement']!=67711058 or row['wmo']!=7543871 or len(joints)!=2 or joints!=row['kerbSteps']
                or max(steps)!=row['maximumStep']):raise ValueError('Unexpected bridge kerb profile')
        limit=.45
    if row['transformError']>.01 or row['portalGap']>.031 or row['maximumStep']>limit or row['minimumHeadroom']<2.2:raise ValueError('Unverified structure contact/clearance')
    if not all(x['permitted'] and not x['hole'] and not x['liquid'] for x in row['landings']):raise ValueError('Missing dry landing')
    if any(abs(x.get('terrainDelta',0))>.300001 for x in row['landings']):raise ValueError('Excessive deck-to-ground step')
    points=row['worldCenterline'];samples=row['samples'];faces=row['faces']
    for f in faces:
        if f.get('nativeRiser'):
            flags=f.get('sourceFlags',0)
            if not (flags&8 or flags&32 and not flags&4) or max(p[2] for p in f['v'])-min(p[2] for p in f['v'])>.350001:
                raise ValueError('Unbounded or noncollidable native stair riser')
    def height(p,tri):
        a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:return
        u=((b[1]-c[1])*(p[0]-c[0])+(c[0]-b[0])*(p[1]-c[1]))/den
        v=((c[1]-a[1])*(p[0]-c[0])+(a[0]-c[0])*(p[1]-c[1]))/den
        weights=[max(0,u),max(0,v),max(0,1-u-v)];total=sum(weights);weights=[x/total for x in weights]
        q=[sum(weight*vertex[axis] for weight,vertex in zip(weights,tri)) for axis in range(3)]
        if math.dist(q[:2],p[:2])>.02:return
        return q[2]
    if len(points)<3 or len(samples)<len(points):raise ValueError('No floor samples')
    for p in points:
        if not all(math.isfinite(v) for v in p) or not any((z:=height(p,f['v'])) is not None and abs(z-p[2])<=.3 for f in faces):raise ValueError('Unsupported centerline vertex')
    for index,s in enumerate(samples):
        p=s['point']
        segment=s['segment']
        if not isinstance(segment,int) or not 0<=segment<len(points)-1:raise ValueError('Invalid sample segment')
        a,b=points[segment],points[segment+1];dx,dy=b[0]-a[0],b[1]-a[1];length=dx*dx+dy*dy
        t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length)) if length else 0
        if math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)>.02:raise ValueError('Floor samples do not support the emitted centerline')
        if s['headroom']<2.2 or not any((z:=height(p,f['v'])) is not None and abs(z-p[2])<.02 for f in faces):raise ValueError(f'Unsupported floor/headroom sample: {row["name"]} {index} {p}')
    if max(math.dist(a['point'][:2],b['point'][:2]) for a,b in zip(samples,samples[1:]))>.251:raise ValueError('Unsampled floor gap')
    return sum(math.dist(a[:2],b[:2]) for a,b in zip(points,points[1:]))

def main():
    source=ROOT/'tools/data/native-gate-corridors-70959.json';rows=json.loads(source.read_text())
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
    result={}
    def point(map,p):
        z=zones[map];q=dict(mapID=map,x=(z['west']-p[1])/(z['west']-z['east']),y=(z['north']-p[0])/(z['north']-z['south']))
        if not 0<=q['x']<=1 or not 0<=q['y']<=1:raise ValueError('Landing outside zone bounds')
        return q
    def add_gate(row,name=None):
        a,b,length=validate(row)
        if row['placementUID'] in result:raise ValueError('Duplicate native gate identity')
        result[row['placementUID']]=dict(a=point(row['fromUiMap'],a),b=point(row['toUiMap'],b),distance=length,
            source='native-wmo-floor',wmo=row['wmoRootFDID'],placement=row['placementUID'],samples=len(row['worldCenterline']),
            maximumStep=max(row['maxAdjacentFloorRise'],abs(row['maxAdjacentFloorDrop'])),headroom=row['minimumCenterlineHeadroom'],
            worldA=[a[1],a[0],a[2]],worldB=[b[1],b[0],b[2]],
            heightProfile=[[math.dist(a[:2],p[:2])/length,p[2]] for p in row['worldCenterline'][::10]]+[[1,b[2]]])
        if name:result[row['placementUID']]['name']=name
    for row in rows:add_gate(row)
    curvedSource=ROOT/'tools/data/native-curved-corridors-70959.json'
    bridgeSource=ROOT/'tools/data/native-southfury-bridge-70959.json'
    batchSource=ROOT/'tools/data/native-bridge-batch-70959.json'
    expandedSource=ROOT/'tools/data/native-bridge-expanded-70959.json'
    curvedRows=json.loads(curvedSource.read_text()) if curvedSource.exists() else []
    bridgeRows=json.loads(bridgeSource.read_text())+(json.loads(batchSource.read_text()) if batchSource.exists() else [])
    if expandedSource.exists():bridgeRows += [r for r in json.loads(expandedSource.read_text()) if r.get('isBridgeAsset') and r.get('verificationRevision')==3]
    for row in curvedRows+bridgeRows:
        length=validate_curved(row)
        points=row['worldCenterline'];a,b=points[0],points[-1]
        key=row.get('corridorID',row['placement'])
        if key in result:raise ValueError('Duplicate native corridor identity')
        result[key]=dict(a=point(row['fromUiMap'],a),b=point(row['toUiMap'],b),distance=length,
            source=row.get('source','native-wmo-floor'),wmo=row['wmo'],model=row.get('model',0),placement=row['placement'],samples=len(row['samples']),
            maximumStep=row['maximumStep'],headroom=row['minimumHeadroom'],name=row['name'],
            worldA=[a[1],a[0],a[2]],worldB=[b[1],b[0],b[2]],worldPath=[[p[1],p[0],p[2]] for p in points])
        if row in bridgeRows:
            # Endpoint access additionally requires the extracted central strip
            # to be supported, rather than inferring width from a centerline.
            transverse=row['widthProof']
            radius=transverse['radiusYards'];across=round(2*radius/.25)+1
            if not math.isfinite(radius) or not .5<=radius<=2.5 or transverse['sampleCount']<across*len(row['samples']) or transverse['longitudinalStepYards']>.25 or transverse['lateralStepYards']>.25 or max(abs(transverse['minimumHeightDelta']),abs(transverse['maximumHeightDelta']))>.3:raise ValueError('Missing bridge width proof')
            result[key]['endpointAccess']=True
            result[key]['radius']=radius
            if 'kerbSteps' in row:result[key]['kerbSteps']=len(row['kerbSteps'])
    # Append new placements after older corridors to preserve existing crossing IDs.
    algaz=ROOT/'tools/data/native-dun-algaz-70959.json'
    for row in json.loads(algaz.read_text()):
        if row['maximumFloorGap']>.02 or any(abs(p['exposedRiser'])>.55 for p in row['terrainLandings']):
            raise ValueError('Unsupported Dun Algaz tunnel entrance or floor')
        add_gate(row,'Dun Algaz tunnel')
    # Preserve the ordinals of existing crossings, including Dun Algaz.
    result=dict(sorted(result.items(),key=lambda item:bool(item[1].get('kerbSteps'))))
    def lua(v):
        if isinstance(v,dict):return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'
        if isinstance(v,list):return '{'+','.join(lua(x) for x in v)+'}'
        return json.dumps(v)
    digest=hashlib.sha256(source.read_bytes()+(curvedSource.read_bytes() if curvedSource.exists() else b'')+bridgeSource.read_bytes()+(batchSource.read_bytes() if batchSource.exists() else b'')+(expandedSource.read_bytes() if expandedSource.exists() else b'')+algaz.read_bytes()).hexdigest()
    (ROOT/'Data/Structures.lua').write_text('-- Native floor-supported corridors; see Structures-SOURCES.md.\nlocal _,A=...\nA.StructureData='+lua(dict(version=1,build=70959,proofSha256=digest,corridors=result))+'\n')
    out=ROOT.parent/'output/zone-crossings-70959';out.mkdir(exist_ok=True)
    (out/'structure-corridors.json').write_text(json.dumps(result,indent=2))
    print('Validated native structure corridors:',len(result))

if __name__=='__main__':main()
