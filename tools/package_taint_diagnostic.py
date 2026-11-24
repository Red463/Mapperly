"""Build a passive taint investigation package without changing public metadata."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import re,runpy
root=Path(__file__).resolve().parents[1]
normal=runpy.run_path(str(root/'tools/package.py'))['out']
version=re.search(r'^## Version:\s*(\S+)',(root/'Mapperly.toc').read_text(),re.M).group(1)+'-taintdiagnostic.1'
out=root/'dist'/('Mapperly-'+version+'.zip')
with ZipFile(normal) as source,ZipFile(out,'w',ZIP_DEFLATED) as target:
    for item in source.infolist():
        data=source.read(item.filename)
        if item.filename=='Mapperly/Mapperly.toc':
            toc=re.sub(r'^## Version:.*$','## Version: '+version,data.decode('utf-8'),flags=re.M)
            toc=re.sub(r'^## SavedVariables:.*$','## SavedVariables: MapperlyDB, MapperlyTaintDiagnosticsDB',toc,flags=re.M)
            data=(toc.rstrip()+'\nTaintDiagnostics.lua\n').encode('utf-8')
        target.writestr(item,data)
    target.write(root/'tools/diagnostics/TaintDiagnostics.lua','Mapperly/TaintDiagnostics.lua')
print(out)
