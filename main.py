from pathlib import Path
from MM.Manager import Manager
from MM.StardewValley import StardewValley
from MM.NexusMods.Nexus import NexusMods,NexusModAccount

NexusMods.account = NexusModAccount("azx0025","Nexgamer0@gmail.com")
StardewValley.Dir = Path(r"D:\Program Files (x86)\Steam\steamapps\common\Stardew Valley")

import os

m = Manager()
m.load_mods()
res = m.update_mods(Path(os.getcwd()).joinpath("Mods"))
# res = m.download_all_mods(Path(os.getcwd()).joinpath("Mods"))
# print("#"*30,"idnotfound","#"*30)
# for i in res.idnotfound:
#     print(i.Name)

# print("#"*30,"hidden","#"*30)
# for i in res.hidden:
#     print(i.Name)
#print("#"*30,"updated","#"*30)
#print(res.updated)

print("#"*30,"Não Verificados","#"*30)
for i in res.idnotfound:
    print(i.Name)

print("#"*30,"Atualizados","#"*30)
for i in res.updated:
    print(i.Name)