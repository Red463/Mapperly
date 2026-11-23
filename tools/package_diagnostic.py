"""Build an opt-in diagnostic ZIP without changing the public TOC or runtime."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re
import runpy

root=Path(__file__).resolve().parents[1]
normal=runpy.run_path(str(root/'tools/package.py'))['out']
version=re.search(r'^## Version:\s*(\S+)',(root/'Mapperly.toc').read_text(encoding='utf-8'),re.M).group(1)
diagnostic=version+'-diagnostic.1'
out=root/'dist'/('Mapperly-'+diagnostic+'.zip')
with ZipFile(normal) as source, ZipFile(out,'w',ZIP_DEFLATED) as target:
    for item in source.infolist():
        data=source.read(item.filename)
        if item.filename=='Mapperly/Mapperly.toc':
            toc=data.decode('utf-8')
            toc=re.sub(r'^## Version:.*$', '## Version: '+diagnostic,toc,flags=re.M)
            toc=re.sub(r'^## Title:.*$', '## Title: Mapperly (Diagnostics)',toc,flags=re.M)
            toc=re.sub(r'^## SavedVariables:.*$', '## SavedVariables: MapperlyDB, MapperlyDiagnosticsDB',toc,flags=re.M)
            data=(toc.rstrip()+'\nDiagnostics.lua\n').encode('utf-8')
        target.writestr(item,data)
    target.write(root/'tools/diagnostics/Diagnostics.lua','Mapperly/Diagnostics.lua')
    target.write(root/'tools/diagnostics/DIAGNOSTICS.txt','Mapperly/DIAGNOSTICS.txt')
print(out)
