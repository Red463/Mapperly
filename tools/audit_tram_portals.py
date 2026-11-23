"""Audit the four Deeprun portal destinations; this does not enable a passenger edge."""
from pathlib import Path
import hashlib
import json
from build_services import rows,CACHE,WORLD
ROOT=Path(__file__).resolve().parents[1]

def audit():
    ids={2166,2171,2173,2175};triggers={};safe={}
    for table,row in rows(CACHE/WORLD,{'areatrigger_teleport','world_safe_locs'}):
        ident=int(row['ID'])
        if table=='areatrigger_teleport' and ident in ids:triggers[ident]=row
        elif table=='world_safe_locs' and ident in {1102166,1102171,1102173,1102175}:safe[ident]=row
    assert set(triggers)==ids and len(safe)==4
    result=[]
    for ident in sorted(ids):
        trigger=triggers[ident];destination=safe[int(trigger['PortLocID'])]
        assert int(destination['MapID'])==(0 if ident in (2166,2171) else 369)
        result.append({'triggerID':ident,'name':trigger['Name'],'safeLocID':int(destination['ID']),
            'destination':{'continent':int(destination['MapID']),'north':float(destination['LocX']),'east':float(destination['LocY']),'z':float(destination['LocZ'])},
            'transportSpawnId':destination['TransportSpawnId']})
    return {'version':1,'build':70959,'source':WORLD,'sourceSha256':hashlib.file_digest((CACHE/WORLD).open('rb'),'sha256').hexdigest(),
        'method':'areatrigger_teleport.PortLocID -> world_safe_locs.ID','passengerConnectionVerified':False,'portals':result}

if __name__=='__main__':
    result=audit();target=ROOT/'tools/data/native-tram-portals-70959.json';target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('Audited four server portal destinations; passenger connection remains unbundled.')
