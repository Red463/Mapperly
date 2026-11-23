"""Travel preferences replan transactionally and mixed previews stay honest."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_ui.py'))['lua']
lua.execute('''
assert(A.boatsCheck and A.zeppelinsCheck and A.airshipsCheck,'navigation tab needs the three verified travel choices')
local N=A.Navigation;local start=N.Start;local calls=0
A.Journey.Clear();N.target=nil
N.Start=function(map,x,y,name,options) calls=calls+1;assert(map==1431 and options.mode=='terrain');return true end
N.pending={map=1431,x=.4,y=.6,name='Travel target'}
A.db.navigationMode='terrain';A.db.useBoats=true
A.boatsCheck:SetChecked(false);A.boatsCheck:GetScript('OnClick')(A.boatsCheck)
assert(A.db.useBoats==false and calls==1,'boat preference changes must replan the latest smart destination')
A.db.navigationMode='direct';A.zeppelinsCheck:SetChecked(false);A.zeppelinsCheck:GetScript('OnClick')(A.zeppelinsCheck)
assert(A.db.useZeppelins==false and calls==1,'direct mode must not start walking jobs for transport changes')
N.Start=start;N.pending=nil
local V=A.JourneyView
V.Show({kind='walking',hasTransports=true,name='Island journey',points={{mapID=1431,x=.1,y=.1},{mapID=1431,x=.2,y=.2}},distance=1000,estimatedSeconds=400,coverage='complete',legs={{kind='walk',name='Walk to Ratchet'},{kind='transport',name='Boat: Ratchet to Booty Bay'}}},{map=1431,x=.2,y=.2,name='Island journey'})
assert(V.summary:GetText():find('including transport',1,true),'mixed time cannot be labelled time on foot')
assert(V.warning:GetText():find('boarding',1,true) and V.warning:GetText():find('estimate',1,true))
''')
print('PASS: transport settings, transactional replan and mixed journey wording')
