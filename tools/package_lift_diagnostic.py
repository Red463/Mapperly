"""Package a read-only lift recorder; leave the normal build unchanged."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import re,runpy
root=Path(__file__).resolve().parents[1]
normal=runpy.run_path(str(root/'tools/package.py'))['out']
version=re.search(r'^## Version:\s*(\S+)',(root/'Mapperly.toc').read_text(encoding='utf8'),re.M).group(1)+'-liftdiagnostic.1'
out=root/'dist'/('Mapperly-'+version+'.zip')
with ZipFile(normal) as source,ZipFile(out,'w',ZIP_DEFLATED) as target:
    for item in source.infolist():
        data=source.read(item.filename)
        if item.filename=='Mapperly/Mapperly.toc':
            toc=data.decode('utf8')
            toc=re.sub(r'^## Version:.*$','## Version: '+version,toc,flags=re.M)
            toc=re.sub(r'^## SavedVariables:.*$','## SavedVariables: MapperlyDB, MapperlyLiftDiagnosticsDB',toc,flags=re.M)
            data=(toc.rstrip()+'\nLiftDiagnostics.lua\n').encode('utf8')
        target.writestr(item,data)
    target.write(root/'tools/diagnostics/LiftDiagnostics.lua','Mapperly/LiftDiagnostics.lua')
    target.write(root/'tools/diagnostics/LIFT_DIAGNOSTICS.txt','Mapperly/LIFT_DIAGNOSTICS.txt')
print(out)
