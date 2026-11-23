"""Native road extraction: compressed/uncompressed masks and occlusion."""
from pathlib import Path
import sys,struct
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'));sys.path.insert(0,str(root/'tools'))
from build_roads import decode_alpha, road_texture, tile_roads
assert road_texture('tileset/duskwood/duskwoodcobblestone_s.blp')
assert road_texture('tileset/kalidar/kalidardarnroad_s.blp')
assert not road_texture('tileset/duskwood/duskwooddirt_s.blp')
assert not road_texture(None)
encoded=b''.join(bytes([255,170]) for _ in range(32))+bytes([160,170])
assert decode_alpha(encoded,0,768)==bytes([170])*4096
assert decode_alpha(bytes([99])*4096,0,256)==bytes([99])*4096
assert decode_alpha(bytes([0x31])*2048,0,256)==bytes([17,51])*2048,'legacy four-bit maps must expand low nibble first'
for malformed in [b'\x80\x00',b'\xff',b'\x7f\x01']:
    try:decode_alpha(malformed,0,768)
    except ValueError:pass
    else:raise AssertionError('bad alpha accepted')
def chunk(tag,data):return tag[::-1].encode()+struct.pack('<I',len(data))+data
names={1:'road.blp',2:'grass.blp'}
layers=struct.pack('<4I',0,0,0,0)+struct.pack('<4I',1,256,0,0)
data=chunk('MDID',struct.pack('<2I',1,2))+b''.join(chunk('MCNK',chunk('MCLY',layers)+chunk('MCAL',bytes([255])*4096)) for _ in range(256))
mask,unknown=tile_roads(data,names)
assert not any(mask) and not unknown,'grass must occlude the underlying road'
data=data.replace(bytes([255])*4096,bytes([0])*4096)
mask,unknown=tile_roads(data,names)
assert set(mask)=={255},'base-layer roads must remain when upper layers are transparent'
print('PASS: native road alpha decoding, occlusion and conservative texture classification')
