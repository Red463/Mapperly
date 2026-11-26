"""Every packaged version must have concise matching player-facing notes."""
from pathlib import Path
import importlib.util,re,tempfile
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release_builder',root/'tools/build_release_notes.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
version=re.search(r'^## Version:\s*(\S+)',(root/'Mapperly.toc').read_text(),re.M).group(1)
assert 'version="'+version+'"'in(root/'Data/ReleaseNotes.lua').read_text(encoding='utf8')
with tempfile.TemporaryDirectory(prefix='release-notes-test-',dir=root/'output')as folder:
 p=Path(folder).resolve();assert p.parent==(root/'output').resolve()
 (p/'docs').mkdir();(p/'Data').mkdir()
 (p/'Mapperly.toc').write_text('## Version: 2.0.0\n')
 highlights=p/'docs/release-highlights.md'
 highlights.write_text('## 2.0.0\n\n- A clearer map.\n- Better routes.\n')
 assert m.build(p)==('2.0.0',['A clearer map.','Better routes.'])
 assert 'Better routes.'in(p/'Data/ReleaseNotes.lua').read_text()
 highlights.write_text('## 2.0.0\n\nSource: CHANGELOG.md\n')
 bullets=['Change '+str(i) for i in range(9)]
 (p/'CHANGELOG.md').write_text('## 2.0.0 - 2026-11-26\n'+''.join('- '+b+'\n' for b in bullets)+'## 1.0.0\n- Old release.\n')
 assert m.build(p)==('2.0.0',bullets)
 for body in ['## 1.0.0\n- Old release.\n','## 2.0.0\n','## 2.0.0\n- '+('x'*181)+'\n']:
  highlights.write_text(body)
  try:m.build(p)
  except ValueError:pass
  else:raise AssertionError('missing/overlong update highlights must block packaging')
print('PASS: consolidated release notes match TOC and changelog; missing, empty or overlong highlights are rejected')
