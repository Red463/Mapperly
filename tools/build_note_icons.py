"""Encode generated note artwork as transparent WoW textures and a preview sheet."""
from pathlib import Path
import json
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from PIL import Image,ImageDraw,ImageFont
source=root/'assets/note-icons'
manifest=json.loads((source/'prompts.json').read_text(encoding='utf-8'))
sheet=Image.new('RGB',(960,660),(31,34,39));draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
labels={'Enemy':'Enemy','Chest':'Chest / loot','POI':'Point of interest','Scenic':'Scenic spot','Building':'Building','Danger':'Area to avoid','Camp':'Camp / rest','Meeting':'Meeting point','Resource':'Resources','Fishing':'Fishing','Cave':'Cave','Travel':'Travel / route'}
draw.text((24,18),'MAPPERLY  -  CUSTOM NOTE ICONS',font=font,fill=(238,207,142))
for i,entry in enumerate(manifest['icons']):
    name=entry['name'];image=Image.open(source/(name+'.png')).convert('RGBA')
    assert image.getchannel('A').getextrema()[0]==0,name+' needs transparency'
    bounds=image.getchannel('A').point(lambda a:255 if a>=32 else 0).getbbox()
    assert bounds,name
    artwork=image.crop(bounds)
    for size,folder in [(128,''),(64,'Medium'),(32,'Small')]:
        icon=artwork.copy();icon.thumbnail((size*15//16,size*15//16),Image.Resampling.LANCZOS)
        result=Image.new('RGBA',(size,size));result.paste(icon,((size-icon.width)//2,(size-icon.height)//2))
        out=root/'Media/Markers'/folder;out.mkdir(exist_ok=True,parents=True)
        result.save(out/('Note'+name+'.tga'),compression=None)
    x=24+(i%4)*234;y=58+(i//4)*196
    icon=artwork.copy();icon.thumbnail((116,116),Image.Resampling.LANCZOS)
    sheet.paste(icon,(x+(190-icon.width)//2,y),icon)
    draw.text((x,y+120),labels[name],font=font,fill=(239,222,181))
    # Show the actual encoded small texture at native marker sizes on parchment.
    draw.rectangle((x,y+147,x+190,y+181),fill=(160,130,75))
    native=Image.open(root/'Media/Markers/Small'/('Note'+name+'.tga')).convert('RGBA')
    for j,size in enumerate([18,24,32]):
        marker=native.resize((size,size),Image.Resampling.LANCZOS)
        sheet.paste(marker,(x+8+j*62,y+148+(32-size)//2),marker)
    print(name+': transparent 128/64/32px TGA')
sheet.save(source/'preview.png')
