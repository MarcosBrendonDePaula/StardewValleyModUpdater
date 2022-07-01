from pyparsing import Path
import json5
import shutil
import pickle
import zipfile
from tqdm import tqdm
import time

from .StardewValley import StardewValley
from .Mod import Mod

from .NexusMods.Nexus import GameId, NexusMods, NexusModAccount

import os

import errno, os, stat, shutil

def handleRemoveReadonly(func, path, exc):
  excvalue = exc[1]
  if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
      os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
      func(path)
  else:
      raise

class ResultModList():
    def __init__(self):
        self.updated = []
        self.hidden = []
        self.idnotfound = []
        self.download = []

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
        pbar = tqdm(total=len(self.Mods))
        for i in self.Mods:
            if (i.NUKP >= 0) and (not cache_objs.get(i.UniqueID) == True):
                if( (i.UpdateKeys[i.NUKP] == "???") or (i.UpdateKeys[i.NUKP] == "-1")):
                    pass
                else:
                    info:dict = N.get_mod_info(GId=GameId.STARDEWVALLEY,ModId=i.UpdateKeys[i.NUKP])
                    if(not info["hidden"]):
                        pbar.desc = "Downloading: {0}".format(i.Name)
                        F_file = output.joinpath("{0} v{1}.zip".format(i.Name,info["version"]))
                        N.download_file(info["download_url"],F_file)
                        Res.download.append(i)
                    else:
                        Res.hidden.append(i)
            else:
                Res.idnotfound.append(i)
            cache_objs[i.UniqueID] = True
            if(use_cache):
                with open(cache_dir, 'wb') as f:
                    pickle.dump(cache_objs,f)
                    f.close()
            pbar.update()
        pbar.close()
        return Res
    def download_mod(
        self,
        mod:Mod,output:Path = Path(os.getcwd())
    )->ResultModList:
        if not output.is_dir():
            print("output is not a directory")
            return
        m = ResultModList()
        N = NexusMods()
        N.login()
        if (mod.NUKP >= 0):
            if( (mod.UpdateKeys[mod.NUKP] == "???") or (mod.UpdateKeys[mod.NUKP] == "-1")):
                pass
            else:
                info:dict = N.get_mod_info(GId=GameId.STARDEWVALLEY,ModId=mod.UpdateKeys[mod.NUKP])
                if(not info["hidden"]):
                    F_file = output.joinpath("{0} v{1}.zip".format(mod.Name,info["version"]))
                    N.download_file(info["download_url"],F_file)
                    m.download.append(mod)
                else:
                    m.hidden.append(mod)
        else:
            m.idnotfound(mod)
        return m
    def update_mods(
        self,temp_dir:Path = Path(os.getcwd()),
        proxie=None
    )->ResultModList:
        output = temp_dir
        
        Res = ResultModList()
        N = NexusMods(proxie=proxie)
        N.login()
        if not output.is_dir():
            print("output is not a directory")
            return
        i:Mod = Mod()
        pbar = tqdm(total=len(self.Mods),leave=True)
        for i in self.Mods:
            if (i.NUKP >= 0):
                if( (i.UpdateKeys[i.NUKP] == "???") or (i.UpdateKeys[i.NUKP] == "-1")):
                    pass
                else:
                    pbar.desc = "checking: {0} ...".format(i.Name)
                    info:dict = N.get_mod_info(GId=GameId.STARDEWVALLEY,ModId=i.UpdateKeys[i.NUKP])
                    if(not info["hidden"]):
                        if i.Version != info["version"]:
                            pbar.desc = "updating: {0} ...".format(i.Name)
                            F_file = output.joinpath("{0} v{1}.zip".format(i.Name,info["version"]))
                            N.download_file(info["download_url"],F_file)

                            # M_dir = str(i.Directory).split("\\Stardew Valley\\mods\\")
                            # parts = M_dir[1].split("\\")
                            # if (len(parts) > 1):
                            #     shutil.rmtree(StardewValley.Dir.joinpath("mods",parts[0]))
                            # else:
                            shutil.rmtree(i.Directory, ignore_errors=False, onerror=handleRemoveReadonly)
                            with zipfile.ZipFile(F_file, 'r') as zipObj:
                                listOfFileNames = zipObj.namelist()
                                for fileName in listOfFileNames:
                                    if not fileName.endswith('ktop.ini') :
                                        zipObj.extract(fileName,StardewValley.Dir.joinpath("mods"))
                            # with zipfile.ZipFile(F_file, 'r') as zip_ref:
                            #     zip_ref.extractall(StardewValley.Dir.joinpath("mods"))
                            Res.updated.append(i)
                    else:
                        Res.hidden.append(i)
            else:
                Res.idnotfound.append(i)
            pbar.update()
        return Res