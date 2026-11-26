from pathlib import Path
import sys,math
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from bridge_geometry import rotate, Mesh, floor_path, quaternion, unplaced, placement_error, placed, collision_triangles, group_header
import struct

names = b'\0bridge32\0Temple\0'
header = struct.pack('<ii', 1, 10) + bytes(60)
assert group_header(struct.pack('<4sI', b'PGOM', 68) + header, names) == (76, 76, 'bridge32', 'Temple')
indices = struct.pack('<3H', 2, 0, 1) * 3
for tag, fmt, material in [('MOPY', '<2B', 255), ('MPY2', '<2H', 65535)]:
    attributes = b''.join(struct.pack(fmt, flag, material) for flag in (8, 36, 32))
    assert list(collision_triangles({'MOVI': indices, tag: attributes})) == [
        (0, (2, 0, 1), 8), (2, (2, 0, 1), 32)]
    try:
        list(collision_triangles({'MOVI': indices[:6], tag: attributes}))
    except ValueError:
        pass
    else:
        raise AssertionError('Truncated triangle list was accepted')
placement=dict(kind='m2',flags=0,scale=1536,pos=[12345.,-45.,16543.],rot=[21.,42.,17.])
vertices=[[1.,2.,3.],[-10.,6.,-7.],[0.,0.,0.]]
for v in vertices:assert math.dist(unplaced(placed(v,placement),placement),v)<1e-9
assert placement_error(vertices,placement)<1e-8
assert math.dist(rotate([1,2,3],[0,0,0]),[1,2,3])<1e-9
assert math.dist(rotate([1,0,0],[0,90,0]),[0,1,0])<1e-9
assert math.dist(rotate([0,0,1],[90,0,0]),[1,0,0])<1e-9
assert math.dist(quaternion([1,0,0],[0,0,math.sin(math.pi/4),math.cos(math.pi/4)]),[0,1,0])<1e-9
mesh=Mesh.from_faces([dict(v=[[0,0,0],[10,0,0],[0,10,0]],group=1,triangle=0,flags=8),dict(v=[[0,0,3],[0,10,3],[10,0,3]],group=1,triangle=1,flags=8)])
assert mesh.floor(2,2)==(0,0,3)
assert mesh.floor(11,11) is None
layered=Mesh.from_faces([dict(v=[[0,0,z],[10,0,z],[0,10,z]],group=1,triangle=i,flags=8) for i,z in enumerate((0,2))])
assert layered.floor(2,2,near=2)[0]==2,'follow the continuous deck instead of dropping to a lower overlapping floor'
assert mesh.gap([2,2,0],[3,2,0])<1e-8
broken=Mesh.from_faces([dict(v=[[x,0,0],[x+4,0,0],[x,4,0]],group=1,triangle=i,flags=8)for i,x in enumerate((0,6))])
assert broken.gap([1,.5,0],[9,.5,0])>2, 'dense samples cannot replace an interval proof across a floor gap'
def rect(x0,y0,x1,y1):
 return [dict(v=[[x0,y0,0],[x1,y0,0],[x1,y1,0]],group=1,triangle=0,flags=8),dict(v=[[x0,y0,0],[x1,y1,0],[x0,y1,0]],group=1,triangle=1,flags=8)]
curved=Mesh.from_faces(rect(0,0,3,8)+rect(0,5,10,8)+rect(7,0,10,8))
path=floor_path(curved,[1.5,1.5,0],[8.5,1.5,0])
assert path and max(p[1]for p in path)>5,'follow the winding native floor rather than bridge an empty chord'
assert floor_path(broken,[1,.5,0],[9,.5,0]) is None
print('PASS: native ZYX rotations, collision floor/ceiling and explicit unsupported space')
