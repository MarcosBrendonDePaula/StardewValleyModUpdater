from pathlib import Path
from MM.Manager import Manager
from MM.StardewValley import StardewValley
from MM.NexusMods.Nexus import NexusMods,NexusModAccount

NexusMods.account = NexusModAccount("user","passw")
StardewValley.Dir = Path("C:\\Users\\nexga\\Desktop\\teste")

import os

m = Manager()
m.load_mods()
res = m.download_all_mods(Path(os.getcwd()).joinpath("Mods"))
print("#"*30,"idnotfound","#"*30)
for i in res.idnotfound:
    print(i.Name)

print("#"*30,"hidden","#"*30)
for i in res.hidden:
    print(i.Name)
#print("#"*30,"updated","#"*30)
#print(res.updated)