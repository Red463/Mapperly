"""Check SQL extraction against quoted names, multiple rows and NULL overrides."""
import importlib.util
from pathlib import Path
import tempfile
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_services',root/'tools/build_services.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sql="""CREATE TABLE `creature` (
  `id` int NOT NULL,
  `name` text,
  `npcflag` int DEFAULT NULL,
) ENGINE=InnoDB;
INSERT INTO `creature` VALUES (1,'Innkeeper O\\'Neil (Harbor)',NULL),(2,'Inn, East',65536);
CREATE TABLE `ignored` (
  `id` int NOT NULL,
) ENGINE=InnoDB;
INSERT INTO `ignored` VALUES (99);
"""
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'source.sql'
    path.write_text(sql,encoding='utf-8')
    result=list(module.rows(path,{'creature'}))
assert len(result)==2
assert result[0][1]=={'id':'1','name':"Innkeeper O'Neil (Harbor)",'npcflag':None}
assert result[1][1]['name']=='Inn, East' and result[1][1]['npcflag']=='65536'
print('PASS: SQL extractor preserves quoted names, extended rows and NULL overrides')
