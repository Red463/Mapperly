"""Slice the generated transparent atlas and encode uncompressed WoW textures."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from PIL import Image

names=['Boat','Zeppelin','Airship','Portal','Dungeon','Mail','Note','ZoneExit']
source=Image.open(root/'assets/marker-atlas.png').convert('RGBA')
assert source.size==(1536,1024)
destination=root/'Media/Markers'
destination.mkdir(exist_ok=True)
def encode(name,tile):
    # Use solid artwork to find bounds, ignoring isolated near-transparent noise.
    bounds=tile.getchannel('A').point(lambda a:255 if a>=32 else 0).getbbox()
    assert bounds is not None
    cropped=tile.crop(bounds)
    for size,folder in [(128,''),(64,'Medium'),(32,'Small')]:
        icon=cropped.copy();icon.thumbnail((size*15//16,size*15//16),Image.Resampling.LANCZOS)
        result=Image.new('RGBA',(size,size))
        result.paste(icon,((size-icon.width)//2,(size-icon.height)//2))
        out=destination/folder;out.mkdir(exist_ok=True)
        result.save(out/(name+'.tga'),compression=None)
        assert result.getchannel('A').getextrema()[0]==0
        for point in [(0,0),(size-1,0),(0,size-1),(size-1,size-1)]: assert result.getpixel(point)[3]==0
    print(name,'128/64/32px RGBA; transparent corners')

for i,name in enumerate(names):
    x,y=(i%4)*384,(i//4)*512
    tile=Image.open(root/'assets/Dungeon-balanced.png').convert('RGBA') if name=='Dungeon' else source.crop((x,y,x+384,y+512))
    encode(name,tile)
for name in ['Hearthstone','FlightMaster','Quest','Destination']:
    encode(name,Image.open(root/'assets'/f'{name}.png').convert('RGBA'))
