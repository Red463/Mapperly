"""Compile separately audited native harbour walking corridors."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'))
from lupa.lua51 import LuaRuntime
from build_structure_corridors import validate_curved

def build():
    source=ROOT/'tools/data/native-harbour-corridors-70959.json'
    rows=json.loads(source.read_text(encoding='utf8'))
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
    lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={}')
    for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Terrain.lua','WalkingRegions.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/f).read_text(encoding='utf8'))
    result={}
    for row in rows:
        length=validate_curved(row);raw=row['worldCenterline'];points=[]
        for mid,p,landing in [(row['fromUiMap'],raw[0],row['landings'][0]),(row['toUiMap'],raw[-1],row['landings'][-1])]:
            z=zones[mid];q=dict(mapID=mid,x=(z['west']-p[1])/(z['west']-z['east']),y=(z['north']-p[0])/(z['north']-z['south']))
            lq=lua.table_from(q)
            assert lua.globals().A.Terrain.Segment(lq,lq)
            assert lua.globals().A.WalkingRegions.Get(lq)==landing['region']
            points.append(q)
        result[row['corridorID']]=dict(a=points[0],b=points[1],distance=length,source='native-wmo-floor',
            name=row['name'],wmo=row['wmo'],placement=row['placement'],samples=len(row['samples']),
            maximumStep=row['maximumStep'],headroom=row['minimumHeadroom'],
            worldA=[raw[0][1],raw[0][0],raw[0][2]],worldB=[raw[-1][1],raw[-1][0],raw[-1][2]],
            worldPath=[[p[1],p[0],p[2]] for p in raw])
    return dict(version=1,build=70959,proofSha256=hashlib.sha256(source.read_bytes()).hexdigest(),corridors=result)

def literal(v):
    if isinstance(v,dict):return '{'+','.join('['+literal(k)+']='+literal(x) for k,x in v.items())+'}'
    if isinstance(v,list):return '{'+','.join(literal(x) for x in v)+'}'
    return json.dumps(v)

if __name__=='__main__':
    data=build()
    script='-- Native harbour access; see HarbourAccess-SOURCES.md.\nlocal _,A=...\nA.HarbourAccessData='+literal(data)+'''
local d=A.HarbourAccessData
if A.StructureData and A.CrossingData and A.StructureData.build==d.build and A.CrossingData.build==d.build then
    for id,row in pairs(d.corridors) do
        A.StructureData.corridors[id]=row
        local found=false
        for _,edge in ipairs(A.CrossingData.edges) do if edge.structure==id then found=true;break end end
        if not found then A.CrossingData.edges[#A.CrossingData.edges+1]={id=#A.CrossingData.edges+1,a=row.a,b=row.b,distance=row.distance,structure=id,source='native-wmo-floor'} end
    end
end
'''
    (ROOT/'Data/HarbourAccess.lua').write_text(script,encoding='utf8')
    print('Harbour corridors:',len(data['corridors']))
