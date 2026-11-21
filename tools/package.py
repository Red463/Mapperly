"""Build an installable ZIP from the TOC version, excluding development files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re

root=Path(__file__).resolve().parents[1]
version=re.search(r"^## Version:\s*(\S+)", (root/'Mapperly.toc').read_text(encoding='utf-8'), re.M).group(1)
if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?",version):
    raise ValueError('Invalid addon version')
out=root/'dist'/('Mapperly-'+version+'.zip')
out.parent.mkdir(exist_ok=True)
source_files={'tools/build_services.py','tools/data/factiontemplate-70959.csv'}
root_docs={'LICENSE','README.md','NOTICE.md','CHANGELOG.md','Mapperly.toc'}
with ZipFile(out,'w',ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        relative=path.relative_to(root)
        if any(part.startswith('.') or part=='__pycache__' for part in relative.parts):
            continue
        include=(len(relative.parts)==1 and (relative.name in root_docs or path.suffix in {'.lua','.xml'}))
        include=include or relative.parts[0] in {'Data','Libs','Media'}
        include=include or (relative.parts[0]=='docs' and 'superpowers' not in relative.parts)
        include=include or relative.as_posix() in source_files
        if include:
            archive.write(path,'Mapperly/'+relative.as_posix())
print(out)
