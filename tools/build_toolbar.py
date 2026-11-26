"""Encode generated transparent toolbar art at native-friendly texture sizes."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent / 'Gatherly/.test-deps'))
from PIL import Image

names = ['Locate', 'AddNote', 'Filters', 'Reveal', 'Lock', 'Settings', 'Resize', 'Compact', 'Close', 'ParentMap', 'Quest', 'Services']
for name in names:
    source = root / 'assets/toolbar' / (name + '.png')
    if name == 'Quest':
        source = root / 'assets/Quest.png'
    elif name == 'Compact':
        source = root / 'assets/toolbar/Compact-v2.png'
    elif name == 'Filters':
        source = root / 'assets/toolbar/Filters-v2.png'
    image = Image.open(source).convert('RGBA')
    bounds = image.getchannel('A').point(lambda a: 255 if a >= 32 else 0).getbbox()
    assert bounds, name
    image = image.crop(bounds)
    for size, folder in [(128, ''), (64, 'Medium'), (32, 'Small')]:
        icon = image.copy()
        icon.thumbnail((size * 15 // 16, size * 15 // 16), Image.Resampling.LANCZOS)
        result = Image.new('RGBA', (size, size))
        result.paste(icon, ((size - icon.width) // 2, (size - icon.height) // 2))
        target = root / 'Media/Toolbar' / folder
        target.mkdir(parents=True, exist_ok=True)
        result.save(target / (name + '.tga'), compression=None)
    print(name, '128/64/32px RGBA')
