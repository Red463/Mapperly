"""Copy supplied branding and encode native-size WoW textures without repainting."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.test-deps'))
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / 'assets/branding'
(root/'Media/Logo.png').write_bytes((source/'Mapperly_Main_850x850.png').read_bytes())
for filename, target, size in [
    ('Mapperly_Icon_32x32.png', 'Icon32.tga', 32),
    ('Mapperly_Icon_64x64.png', 'Icon.tga', 64),
    ('Mapperly_Small_128x128.png', 'Portrait.tga', 128),
]:
    with Image.open(source/filename) as original:
        assert original.size==(size,size), filename
        icon=original.convert('RGBA')
        icon.save(root/'Media'/target, compression=None)
        print(f'{target}: {icon.size}, RGBA; supplied pixels and alpha preserved')
