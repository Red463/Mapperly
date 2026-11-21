"""Build a small standalone service dataset from a pinned Forever SQL snapshot.

Run from the workspace root. No database server or Questie is needed.
The source archive is excluded from release ZIPs; output is plain auditable Lua.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import re
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'assets/services-source'
ARCHIVE='TDB_full_forever_2026_10_14.7z'
URL='https://github.com/Karrz1/TrinityCore/releases/download/forever-tdb-2026-10-14/'+ARCHIVE
SHA256='373cdca7963927d4d67933032b4b858a811eae0af960d4de4ff19833a88d4f41'
WORLD='TDB_full_world_forever_2026_10_14.sql'
HOTFIX='TDB_full_hotfixes_forever_2026_10_14.sql'
TUPLE=re.compile(r"\((?:'(?:\\.|[^'\\])*'|[^'()])*\)")
MAPS={0,1,2991}  # Forever's two continents and Zephras Isle; no retail/instance maps.

def rows(path,wanted):
    """Read mysqldump extended INSERTs using each table's declared columns."""
    schemas={};table=None
    with path.open(encoding='utf-8') as source:
        for line in source:
            if line.startswith('CREATE TABLE `'):
                table=line.split('`')[1]
                if table in wanted: schemas[table]=[]
            elif table in wanted and line.startswith('  `'):
                schemas[table].append(line.split('`')[1])
            elif line.startswith(')'): table=None
            elif line.startswith('INSERT INTO `'):
                name=line.split('`')[1]
                if name not in wanted: continue
                columns=schemas[name]
                payload=line.split(' VALUES ',1)[1]
                for match in TUPLE.finditer(payload):
                    values=next(csv.reader(io.StringIO(match.group()[1:-1]),delimiter=',',quotechar="'",escapechar='\\'))
                    if len(values)!=len(columns): raise ValueError(f'{name}: mismatched SQL columns')
                    yield name,dict(zip(columns,(None if v=='NULL' else v for v in values)))

def number(row,key,default=0):
    value=row.get(key)
    return float(value) if value is not None else default

def build():
    CACHE.mkdir(parents=True,exist_ok=True)
    archive=CACHE/ARCHIVE
    if not archive.exists(): urllib.request.urlretrieve(URL,archive)
    with archive.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==SHA256
    for filename in [WORLD]:
        if not (CACHE/filename).exists(): subprocess.run(['tar','-xf',str(archive),'-C',str(CACHE),filename],check=True)
    with (ROOT/'tools/data/factiontemplate-70959.csv').open(encoding='utf-8-sig',newline='') as f:
        factions={int(r['ID']):r for r in csv.DictReader(f)}
    def access(faction):
        f=factions.get(int(faction or 0))
        if not f: return 'AH' if not faction else None
        group=int(f['FactionGroup']);friends=int(f['FriendGroup']);enemies=int(f['EnemyGroup'])
        if (group|friends)&2 and not (group|friends)&4 and enemies&4: return 'A'
        if (group|friends)&4 and not (group|friends)&2 and enemies&2: return 'H'
        if enemies&6==0: return 'AH'
        if enemies&2 and not enemies&4: return 'H'
        if enemies&4 and not enemies&2: return 'A'
        return None
    templates={};spawns=[];addons={};skipped_phased=0
    tables={'creature','creature_template','gameobject','gameobject_template','gameobject_template_addon'}
    for table,r in rows(CACHE/WORLD,tables):
        if table=='creature_template':
            if int(r['npcflag'])&65536: templates[('inn',int(r['entry']))]=(r['name'],int(r['faction']))
        elif table=='gameobject_template':
            if int(r['type'])==19: templates[('mail',int(r['entry']))]=(r['name'],0)
        elif table=='gameobject_template_addon': addons[int(r['entry'])]=int(r['faction'])
        else:
            if int(r['map']) not in MAPS: continue
            if any(number(r,k)!=0 for k in ['PhaseId','PhaseGroup','phaseUseFlags']):
                skipped_phased+=1;continue
            spawns.append((table,r))
    result=[];seen=set()
    for table,r in spawns:
        category='inn' if table=='creature' else 'mail';entry=int(r['id'])
        template=templates.get((category,entry))
        if not template: continue
        if category=='inn' and r.get('npcflag') is not None and not int(r['npcflag'])&65536: continue
        name,faction=template
        if category=='mail': faction=addons.get(entry,0)
        x,y=number(r,'position_x'),number(r,'position_y')
        instance=int(r['map'])
        key=(category,entry,instance,round(x,1),round(y,1))
        if key in seen: continue
        seen.add(key)
        result.append(dict(category=category,id=entry,name=name,instance=instance,x=round(x,3),y=round(y,3),access=access(faction)))
    result.sort(key=lambda p:(p['category'],p['instance'],p['id'],p['x'],p['y']))
    assert any(p['id']==6790 and p['category']=='inn' for p in result),'Darkshire inn must exist'
    counts={k:sum(p['category']==k for p in result) for k in ['inn','mail']}
    assert counts['inn']>=30 and counts['mail']>=30,counts
    output=['-- Generated by tools/build_services.py. Do not hand-edit.',
            '-- Source: Karrz1/TrinityCore Forever TDB 2026-10-14; GPL-2.0.',
            '-- See Data/Services-SOURCES.md and Libs/Forever-Services-COPYING.txt.',
            'local _,A=...','A.BundledServices={']
    for p in result:
        fields=[]
        for key,value in p.items():
            if value is not None: fields.append(key+'='+json.dumps(value,ensure_ascii=False))
        output.append(' {'+','.join(fields)+'},')
    output.append('}')
    (ROOT/'Data/Services.lua').write_text('\n'.join(output)+'\n',encoding='utf-8')
    report={'source':URL,'sha256':SHA256,'counts':counts,'worldMaps':sorted(MAPS),'unknownFactionRecords':sum(p['access'] is None for p in result),'phasedWorldSpawnsExcluded':skipped_phased,'records':result}
    (CACHE/'service-extract.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))

if __name__=='__main__': build()
