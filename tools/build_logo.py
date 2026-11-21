"""Encode the supplied logo for WoW, preserving its artwork and alpha."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.test-deps'))
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / 'Media/Logo.png'
with Image.open(source) as original:
    logo = original.convert('RGBA')
    logo.thumbnail((256, 256), Image.Resampling.LANCZOS)
    icon = Image.new('RGBA', (256, 256))
    icon.paste(logo, ((256-logo.width)//2, (256-logo.height)//2))
    icon.save(root / 'Media/Icon.tga', compression=None)
    print(f'Icon.tga: {icon.size}, {icon.mode}; source: {original.size}')
