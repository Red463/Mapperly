"""Read-only placed WMO/M2 collision geometry and world-vertical floor probes.

Placement convention: TrinityCore ModelInstance.cpp fromEulerAnglesZYX(y,x,z).
M2 geometry uses native MD20 collision arrays, never render meshes.
"""
from collections import OrderedDict,defaultdict
from pathlib import Path
import hashlib,heapq,math,struct
from build_southfury_bridge import Native,chunks,bary,ORIGIN,T,LocalCasc

def rotate(v,angles):
    pitch,yaw,roll=map(math.radians,angles)
    x,y,z=v
    y,z=math.cos(roll)*y-math.sin(roll)*z,math.sin(roll)*y+math.cos(roll)*z
    x,z=math.cos(pitch)*x+math.sin(pitch)*z,-math.sin(pitch)*x+math.cos(pitch)*z
    return [math.cos(yaw)*x-math.sin(yaw)*y,math.sin(yaw)*x+math.cos(yaw)*y,z]

def placed(v,p):
    r=rotate(v,p['rot']);scale=p['scale']/1024 if p['kind']=='m2' or p['flags']&4 else 1
    return [ORIGIN-p['pos'][2]-scale*r[0],ORIGIN-p['pos'][0]-scale*r[1],p['pos'][1]+scale*r[2]]

def unplaced(v,p):
    scale=p['scale']/1024 if p['kind']=='m2' or p['flags']&4 else 1
    if scale<=0:raise ValueError('Invalid native placement scale')
    x,y,z=(ORIGIN-p['pos'][2]-v[0])/scale,(ORIGIN-p['pos'][0]-v[1])/scale,(v[2]-p['pos'][1])/scale
    pitch,yaw,roll=map(math.radians,p['rot'])
    x,y=math.cos(yaw)*x+math.sin(yaw)*y,-math.sin(yaw)*x+math.cos(yaw)*y
    x,z=math.cos(pitch)*x-math.sin(pitch)*z,math.sin(pitch)*x+math.cos(pitch)*z
    y,z=math.cos(roll)*y+math.sin(roll)*z,-math.sin(roll)*y+math.cos(roll)*z
    return [x,y,z]

def placement_error(vertices,p):
    """Measured numerical roundtrip in world yards, not a convention proof."""
    scale=p['scale']/1024 if p['kind']=='m2' or p['flags']&4 else 1
    return max(math.dist(unplaced(placed(v,p),p),v)*scale for v in vertices)

def quaternion(v,q):
    x,y,z,w=q;vx,vy,vz=v
    tx,ty,tz=2*(y*vz-z*vy),2*(z*vx-x*vz),2*(x*vy-y*vx)
    return [vx+w*tx+y*tz-z*ty,vy+w*ty+z*tx-x*tz,vz+w*tz+x*ty-y*tx]

class Mesh:
    @classmethod
    def from_faces(cls,faces):
        self=cls();self.faces=faces;self.grid=defaultdict(list)
        for i,f in enumerate(faces):
            a,b,c=f['v'];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k]for k in range(3)]
            n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            f['up']=n[2]>0;f['slope']=math.degrees(math.atan2(math.hypot(*n[:2]),abs(n[2])))
            lo=[min(p[k]for p in f['v'])for k in range(2)];hi=[max(p[k]for p in f['v'])for k in range(2)]
            if (hi[0]-lo[0])*(hi[1]-lo[1])>1000000:continue
            for x in range(math.floor(lo[0]/4),math.floor(hi[0]/4)+1):
                for y in range(math.floor(lo[1]/4),math.floor(hi[1]/4)+1):self.grid[x,y].append(i)
        return self

    def floors(self,north,east):
        hits=[]
        for i in self.grid.get((math.floor(north/4),math.floor(east/4)),[]):
            f=self.faces[i];z=bary(north,east,f['v'])
            if z is not None:hits.append((z,i))
        floors=[(z,i) for z,i in hits if self.faces[i]['up'] and self.faces[i]['slope']<=50]
        result=[]
        for z,index in sorted(floors):
            ceilings=[h for h,i in hits if not self.faces[i]['up'] and h>z+.1]
            result.append((z,index,min(ceilings)-z if ceilings else 999))
        return result

    def floor(self,north,east,near=None):
        floors=self.floors(north,east)
        if not floors:return
        return min(floors,key=lambda f:abs(f[0]-near))if near is not None else floors[0]

    def gap(self,a,b):
        """Largest XY interval lacking a matching upward collision triangle."""
        candidates=set()
        for x in range(math.floor(min(a[0],b[0])/4),math.floor(max(a[0],b[0])/4)+1):
            for y in range(math.floor(min(a[1],b[1])/4),math.floor(max(a[1],b[1])/4)+1):candidates.update(self.grid.get((x,y),[]))
        intervals=[]
        for i in candidates:
            f=self.faces[i]
            if not f['up']or f['slope']>50:continue
            u,v,w=f['v'];den=(v[1]-w[1])*(u[0]-w[0])+(w[0]-v[0])*(u[1]-w[1])
            if abs(den)<1e-10:continue
            def weights(p):
                x=((v[1]-w[1])*(p[0]-w[0])+(w[0]-v[0])*(p[1]-w[1]))/den
                y=((w[1]-u[1])*(p[0]-w[0])+(u[0]-w[0])*(p[1]-w[1]))/den
                return [x,y,1-x-y]
            first,last=weights(a),weights(b);lo,hi=0.,1.
            z0=sum(x*p[2]for x,p in zip(first,f['v']))-a[2];z1=sum(x*p[2]for x,p in zip(last,f['v']))-b[2]
            constraints=list(zip(first,last))+[(.3-z0,.3-z1),(.3+z0,.3+z1)]
            for start,end in constraints:
                delta=end-start
                if abs(delta)<1e-12:
                    if start<-.0000001:lo=1;hi=0;break
                elif delta>0:lo=max(lo,(-.0000001-start)/delta)
                else:hi=min(hi,(-.0000001-start)/delta)
            if lo<=hi:intervals.append((lo,hi))
        cursor=0.;largest=0.
        for lo,hi in sorted(intervals):
            largest=max(largest,lo-cursor);cursor=max(cursor,hi)
        return max(largest,1-cursor)*math.dist(a[:2],b[:2])

def floor_path(mesh,start,end,limit=20000):
    """Bounded layered floor search; every edge needs native interval support."""
    step=.5;initial=(0,0,round(start[2]*100));positions={initial:start};cost={initial:0};previous={};queue=[(math.dist(start[:2],end[:2]),0,initial)]
    visited=set();cache={}
    def hits(x,y):
        key=x,y
        if key not in cache:cache[key]=mesh.floors(start[0]+x*step,start[1]+y*step)
        return cache[key]
    while queue and len(visited)<limit:
        _,g,key=heapq.heappop(queue)
        if key in visited or g!=cost[key]:continue
        visited.add(key);p=positions[key]
        if math.dist(p[:2],end[:2])<=.75 and abs(p[2]-end[2])<=.9 and mesh.gap(p,end)<=.03:
            result=[end,p]
            while key in previous:key=previous[key];result.append(positions[key])
            return list(reversed(result))
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
            x,y=key[0]+dx,key[1]+dy
            for z,face,headroom in hits(x,y):
                if headroom<2.2 or abs(z-p[2])>.9:continue
                q=[start[0]+x*step,start[1]+y*step,z];target=x,y,round(z*100)
                if target in visited:continue
                candidate=g+math.dist(p,q)
                if candidate>=cost.get(target,math.inf):continue
                # Reserve a small actor-width disk except at the exact handoffs.
                if min(math.dist(q[:2],start[:2]),math.dist(q[:2],end[:2]))>1:
                    clear=True
                    for i in range(8):
                        a=i*math.pi/4;h=mesh.floor(q[0]+.55*math.cos(a),q[1]+.55*math.sin(a),near=z)
                        if not h or h[2]<2.2 or abs(h[0]-z)>.3:clear=False;break
                    if not clear:continue
                if mesh.gap(p,q)>.03:continue
                positions[target]=q;cost[target]=candidate;previous[target]=key
                heapq.heappush(queue,(candidate+math.dist(q[:2],end[:2]),candidate,target))
    return None

class Reader:
    def __init__(self,snapshot):
        self.casc=LocalCasc(snapshot);self.blobs=OrderedDict();self.hashes={};self.used={};self.assets={};self.samplers={};self.wdts={};self.witnesses={}

    def read(self,fid):
        if fid in self.blobs:b=self.blobs.pop(fid)
        else:b=self.casc.read_fdid(fid);self.hashes[fid]=hashlib.sha256(b).hexdigest()
        self.blobs[fid]=b
        if len(self.blobs)>64:self.blobs.popitem(last=False)
        self.used[fid]=self.hashes[fid];return b

    def sampler(self,mid,wdt):
        raw=self.read(wdt)
        if mid not in self.samplers:
            sampler=Native.__new__(Native);sampler.cache={};sampler.maid=next(raw[a:b]for t,a,b in chunks(raw)if t=='MAID');sampler.read=self.read
            self.samplers[mid]=sampler
        return self.samplers[mid]

    def terrain(self,sampler,n,e):
        result=sampler.terrain(n,e)
        self.used[result['fdid']]=self.hashes[result['fdid']]
        return result

    def witness(self,p,sampler):
        tx,ty=int(p['pos'][0]//T),int(p['pos'][2]//T);tag='MODF' if p['kind']=='wmo' else 'MDDF';size=64 if p['kind']=='wmo' else 36
        for yy in range(max(0,ty-1),min(64,ty+2)):
            for xx in range(max(0,tx-1),min(64,tx+2)):
                ids=struct.unpack_from('<8I',sampler.maid,(yy*64+xx)*32)
                for fid in sorted(set(v for v in ids[:3]if v)):
                    key=fid,tag
                    if key not in self.witnesses:
                        blob=self.read(fid);rows={}
                        for t,a,b in chunks(blob):
                            if t==tag:
                                for at in range(a,b,size):rows[struct.unpack_from('<I',blob,at+4)[0]]=blob[at:at+size]
                        self.witnesses[key]=rows
                    raw=self.witnesses[key].get(p['uid'])
                    if raw:
                        self.used[fid]=self.hashes[fid]
                        if struct.unpack_from('<I',raw)[0]!=p['fdid'] or list(struct.unpack_from('<3f',raw,8))!=p['pos'] or list(struct.unpack_from('<3f',raw,20))!=p['rot']:raise ValueError('Native placement mismatch')
                        scale,flags=(struct.unpack_from('<H',raw,62)[0],struct.unpack_from('<H',raw,56)[0]) if tag=='MODF' else struct.unpack_from('<2H',raw,32)
                        if scale!=p['scale'] or flags!=p['flags']:raise ValueError('Native placement flags/scale mismatch')
                        if tag=='MODF' and list(struct.unpack_from('<6f',raw,32))!=p['bounds']:raise ValueError('Native bounds mismatch')
                        if tag=='MODF':p['doodadSet']=struct.unpack_from('<H',raw,58)[0]
                        return
        raise ValueError('No native placement witness near origin')

    def asset(self,kind,fid):
        key=kind,fid
        if key in self.assets:
            result=self.assets[key];self.used.update(result['sources']);return result
        before=dict(self.used);raw=self.read(fid);faces=[];vertices=[];embedded=[];sets=[];bridge_groups=[]
        if kind=='m2':
            at=raw.find(b'MD20')
            if at<0:raise ValueError('Missing MD20 collision header')
            ni,oi,nv,ov=struct.unpack_from('<4I',raw,at+216)
            if not ni or not nv:raise ValueError('Model has no collision triangles')
            if ni%3 or at+oi+ni*2>len(raw) or at+ov+nv*12>len(raw):raise ValueError('Invalid collision arrays')
            vertices=list(struct.iter_unpack('<3f',raw[at+ov:at+ov+nv*12]))
            for i,ids in enumerate(struct.iter_unpack('<3H',raw[at+oi:at+oi+ni*2])):
                faces.append(dict(v=[vertices[k]for k in ids],group=fid,triangle=i,flags=8))
        else:
            root={t:raw[a:b]for t,a,b in chunks(raw)};count=struct.unpack_from('<I',root['MOHD'],4)[0]
            groups=struct.unpack_from('<'+'I'*count,root['GFID'])
            names=root.get('MOGN',b'')
            for index,at in enumerate(range(0,len(root.get('MOGI',b'')),32)):
                offset=struct.unpack_from('<i',root['MOGI'],at+28)[0]
                name=names[offset:].split(b'\0',1)[0].decode('utf8','replace')if offset>=0 else ''
                if 'bridge'in name.lower()and index<len(groups):bridge_groups.append(groups[index])
            if len(groups)>64:groups=tuple(bridge_groups)
            for group_id in groups:
                group_raw=self.read(group_id);a,b=next((a,b)for t,a,b in chunks(group_raw)if t=='MOGP')
                gc={t:group_raw[c:d]for t,c,d in chunks(group_raw,a+68,b)}
                vs=list(struct.iter_unpack('<3f',gc.get('MOVT',b'')));vertices.extend(vs)
                if not gc.get('MOPY'):continue
                for i,(ids,(flags,material)) in enumerate(zip(struct.iter_unpack('<3H',gc['MOVI']),struct.iter_unpack('<2B',gc['MOPY']))):
                    if flags&8 or flags&32 and not flags&4:faces.append(dict(v=[vs[k]for k in ids],group=group_id,triangle=i,flags=flags))
            models=list(struct.iter_unpack('<I',root.get('MODI',b'')))
            for at in range(0,len(root.get('MODS',b'')),32):sets.append(struct.unpack_from('<2I',root['MODS'],at+20))
            for i,at in enumerate(range(0,len(root.get('MODD',b'')),40)):
                blob=root['MODD'];index=struct.unpack_from('<I',blob,at)[0]&0xffffff
                if index<len(models):embedded.append(dict(index=i,fdid=models[index][0],pos=struct.unpack_from('<3f',blob,at+4),quaternion=struct.unpack_from('<4f',blob,at+16),scale=struct.unpack_from('<f',blob,at+32)[0]))
        if not faces and not embedded:raise ValueError('No collidable faces')
        result=dict(vertices=vertices,faces=faces,embedded=embedded,sets=sets,bridgeGroups=bridge_groups,sources={k:v for k,v in self.used.items()if k not in before or k==fid})
        # Include cached group reads too, even if another placement used them.
        if kind=='wmo':result['sources'].update({g:self.hashes[g]for g in groups})
        self.assets[key]=result;return result

    def parts(self,p):
        asset=self.asset(p['kind'],p['fdid'])
        if p['kind']!='wmo':return []
        active={0,p.get('doodadSet',0)};indices=set()
        for set_id in active:
            if set_id<len(asset['sets']):
                start,count=asset['sets'][set_id];indices.update(range(start,start+count))
        return ['group:'+str(g)for g in asset['bridgeGroups']]+['doodad:'+str(e['index'])for e in asset['embedded']if e['index']in indices and e['fdid']in p.get('embeddedCandidates',[])]

    def mesh(self,p,sampler,part=None):
        if p.get('components'):
            meshes=[]
            for component in p['components']:
                mesh,asset,slack=self.mesh(component,sampler);meshes.append(mesh)
            faces=[f for mesh in meshes for f in mesh.faces];vertices=[v for f in faces for v in f['v']]
            center=[sum(v[k]for v in vertices)/len(vertices)for k in range(2)]
            xx=sum((v[0]-center[0])**2 for v in vertices);yy=sum((v[1]-center[1])**2 for v in vertices);xy=sum((v[0]-center[0])*(v[1]-center[1])for v in vertices)
            angle=.5*math.atan2(2*xy,xx-yy);dn,de=math.cos(angle),math.sin(angle)
            extents=[(v[0]-center[0])*dn+(v[1]-center[1])*de for v in vertices]
            ends=[[center[0]+t*dn,center[1]+t*de,0]for t in(min(extents),max(extents))]
            model=next((c['fdid']for c in p['components']if c['kind']=='m2'),0)
            return Mesh.from_faces(faces),dict(vertices=vertices,faces=faces,axisEnds=ends,source='native-model-floor'if model else 'native-wmo-floor',model=model),None
        self.witness(p,sampler);asset=self.asset(p['kind'],p['fdid'])
        if part and part.startswith('group:'):
            group=int(part.split(':')[1]);local_faces=[f for f in asset['faces']if f['group']==group]
            asset=dict(asset,faces=local_faces,vertices=[v for f in local_faces for v in f['v']])
        if part and part.startswith('doodad:'):
            if part not in self.parts(p):raise ValueError('Doodad is not in the active native set')
            e=next(e for e in asset['embedded']if e['index']==int(part.split(':')[1]));model=self.asset('m2',e['fdid'])
            def local(v):return [a+e['scale']*b for a,b in zip(e['pos'],quaternion(v,e['quaternion']))]
            values=model['vertices'];axis=max(range(2),key=lambda k:max(v[k]for v in values)-min(v[k]for v in values))
            low=[(min(v[k]for v in values)+max(v[k]for v in values))/2 for k in range(3)];high=list(low)
            low[axis]=min(v[axis]for v in values);high[axis]=max(v[axis]for v in values)
            asset=dict(asset,vertices=[local(v)for v in values],faces=[dict(f,v=[local(v)for v in f['v']])for f in model['faces']],axisEnds=[placed(local(v),p)for v in (low,high)],model=e['fdid'],source='native-model-floor')
        if not asset['vertices']or not asset['faces']:raise ValueError('No selected collision geometry')
        faces=[dict(f,v=[placed(v,p)for v in f['v']])for f in asset['faces']]
        vs=[placed(v,p)for v in asset['vertices']]
        slack=None
        if p['kind']=='wmo':
            actual=[ORIGIN-max(v[1]for v in vs),min(v[2]for v in vs),ORIGIN-max(v[0]for v in vs),ORIGIN-min(v[1]for v in vs),max(v[2]for v in vs),ORIGIN-min(v[0]for v in vs)]
            slack=[actual[i]-p['bounds'][i]if i<3 else p['bounds'][i]-actual[i]for i in range(6)]
            if min(slack)<-.02:raise ValueError('Full rotation fails native bounds containment')
        return Mesh.from_faces(faces),asset,slack
