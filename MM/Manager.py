from pyparsing import Path
import json5
import datetime
import pickle

from .StardewValley import StardewValley
from .Mod import Mod

from .NexusMods.Nexus import GameId, NexusMods, NexusModAccount

import os

class ResultModList():
    def __init__(self):
        self.updated = []
        self.hidden = []
        self.idnotfound = []

class Manager():
    def __init__(self):
        self.Mods:list = []
    
    def load_mod(self,Folder:Path = Path(),InfoJsonFile:Path = Path())->Mod:
        with open(InfoJsonFile, 'r') as f:
            txt = str(f.read())
            try:
                in_pos = txt.find('{')
                txt = txt[in_pos:len(txt)]
                InfoJson = json5.loads(txt)
                return Mod(args=InfoJson, directory = Folder)
            except Exception as e:
                print("-"*30)
                print(Folder)
                print(e)
                print("-"*30)
                return None

    def load_mods(self):
        
        ModsFolder:Path = StardewValley.Dir.joinpath("mods")
        
        if( not ModsFolder.exists()):
            print("mods folder does not exist")
            return
        
        Mods_Folders = os.listdir(ModsFolder)
        
        for folder in Mods_Folders:
            InfoJsonFile:Path = ModsFolder.joinpath(folder,"manifest.json")
            if(not InfoJsonFile.exists()):
                mod_founded = False
                #Checando sub pastas para encontrar mods
                if(ModsFolder.joinpath(folder).is_dir()):
                    subdirs = os.listdir(ModsFolder.joinpath(folder))
                    for s_dir in subdirs:
                        Sub_InfoJsonFile:Path = ModsFolder.joinpath(folder,s_dir,"manifest.json")
                        if(Sub_InfoJsonFile.exists()):
                            mod_founded = True
                            self.Mods.append(self.load_mod(ModsFolder.joinpath(folder),Sub_InfoJsonFile)) 
                    if(not mod_founded):
                        print("manifest.json does not exist in this folder(s) {0}".format(ModsFolder.joinpath(folder)))
            else :
                self.Mods.append(self.load_mod(ModsFolder.joinpath(folder),InfoJsonFile)) 
        i:Mod = Mod()
        for i in self.Mods:
            print(i.UniqueID,i.Name, i.UpdateKeys)
            #print(i.Name,i.Version,i.UpdateKeys)
    
    def download_all_mods(
        self,output:Path = Path(os.getcwd()),
        use_cache=True,
        proxie=None
    )->ResultModList:

        cache_dir:Path=Path(os.getcwd()).joinpath("cache.ch")
        
        cache_objs:dict = {}

        if(use_cache and (not os.path.exists(cache_dir))):
            with open(cache_dir, 'wb') as f:
                pickle.dump(cache_objs,f)
                f.close()
        if(use_cache):
            with open(cache_dir, 'rb') as f:
                cache_objs = pickle.load(f)
                f.close()
        
        Res = ResultModList()
        N = NexusMods(proxie=proxie)
        N.login()
        if not output.is_dir():
            print("output is not a directory")
            return
        i:Mod = Mod()
        for i in self.Mods:
            if (i.NUKP >= 0) and (not cache_objs.get(i.UniqueID) == True):
                if( (i.UpdateKeys[i.NUKP] == "???") or (i.UpdateKeys[i.NUKP] == "-1")):
                    pass
                else:
                    print(i.Name,i.UniqueID,i.UpdateKeys[i.NUKP])
                    info:Dict = N.get_mod_info(GId=GameId.STARDEWVALLEY,ModId=i.UpdateKeys[i.NUKP])
                    current_time = datetime.datetime.now()
                    if(not info["hidden"]):
                        print("_"*100)
                        print(info)
                        print("MS:",datetime.datetime.now() - current_time,"\n")
                        print("#"*100)
                        current_time = datetime.datetime.now()
                        F_file = output.joinpath("{0} v{1}.zip".format(i.Name,info["version"]))
                        N.download_file(info["download_url"],F_file)
                        print("MS:",datetime.datetime.now() - current_time,"\n")
                        Res.updated.append(i)
                    else:
                        Res.hidden.append(i)
            else:
                print(i.Name,"Nexus key not found!")
                Res.idnotfound.append(i)
            cache_objs[i.UniqueID] = True
            if(use_cache):
                with open(cache_dir, 'wb') as f:
                    pickle.dump(cache_objs,f)
                    f.close()
        return Res
