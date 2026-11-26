"""Generate concise in-game update notes from curated player-facing highlights."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def build(root=ROOT):
 version=re.search(r'^## Version:\s*(\S+)',(root/'Mapperly.toc').read_text(encoding='utf8'),re.M).group(1)
 source=(root/'docs/release-highlights.md').read_text(encoding='utf8')
 sections=re.split(r'^## ',source,flags=re.M)
 section=next((s.split('\n',1)[1]for s in sections[1:]if s.split('\n',1)[0].strip()==version),None)
 if section is None:raise ValueError('Add player-facing highlights for '+version+' to docs/release-highlights.md')
 if section.strip()=='Source: CHANGELOG.md':
  changelog=(root/'CHANGELOG.md').read_text(encoding='utf8')
  match=re.search(r'^## '+re.escape(version)+r'(?: - [^\n]+)?\n(.*?)(?=^## |\Z)',changelog,re.M|re.S)
  if not match:raise ValueError('Missing consolidated changelog for '+version)
  section=match.group(1)
 changes=[s[2:].strip()for s in section.splitlines()if s.startswith('- ')]
 if not changes or any(not s or len(s)>180 for s in changes):raise ValueError('Use release highlights of at most 180 characters each')
 output='-- Generated from docs/release-highlights.md; keep current with the TOC.\nlocal _,A=...\nA.ReleaseNotes={version='+json.dumps(version)+',changes={'+','.join(json.dumps(s,ensure_ascii=False)for s in changes)+'}}\n'
 (root/'Data/ReleaseNotes.lua').write_text(output,encoding='utf8')
 return version,changes
if __name__=='__main__':
 version,changes=build();print('Generated',len(changes),'release highlights for',version)
