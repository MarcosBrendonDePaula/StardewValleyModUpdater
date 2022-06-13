
from pathlib import Path
from pyparsing import Dict
from requests import Session

import cloudscraper
from bs4 import BeautifulSoup,Tag
from requests import Response

class NexusModAccount:
    def __init__(self, user:str, password:str):
        self.user = user
        self.password = password
        self.Session:Session = Session()
        self.logged:bool = False
        pass
    pass

class GameId:
    STARDEWVALLEY:int = 1303
    
    @staticmethod
    def Name(GId:int = 0)->str:
        if(GId == GameId.STARDEWVALLEY): 
            return "stardewvalley"
        else: 
            return ""
    
class NexusMods():
    URL:str = "https://www.nexusmods.com/stardewvalley/mods"
    account:NexusModAccount = NexusModAccount("","")

    def __init__(self, Account:NexusModAccount = None,proxie = None):
        if(Account):
            self.Account = Account
        else:
            self.Account:NexusModAccount = NexusMods.account
        self.Account.Session.proxies = proxie
        self.scraper:cloudscraper.CloudScraper = cloudscraper.create_scraper(sess=self.Account)
        pass
    
    def login(self):

        callback = r"https://www.nexusmods.com/oauth/callback"
        referrer = r"https%3A%2F%2Fwww.nexusmods.com%2Fstardewvalley%2Fmods%2F12286%3Ftab%3Dfiles"
        url = r"https://users.nexusmods.com/oauth/authorize?client_id=nexus&redirect_uri={0}&response_type=code&referrer={1}".format(callback,referrer)
        
        res:Response = self.scraper.get(url)
        bs4 = BeautifulSoup(res.content,"lxml")
        
        login_token:str = None
        meta:Tag
        for meta in bs4.find_all("meta"):
            if(meta.attrs["name"] == "csrf-token"):
                login_token = meta.attrs["content"]
        if not login_token == None:
            
            payload = {
               "authenticity_token":login_token,
               "user[login]":self.Account.user,
               "user[password]":self.Account.password,
               "commit":"Log in"
            }

            res:Response = self.scraper.post("https://users.nexusmods.com/auth/sign_in",data=payload)
            res:Response = self.scraper.get("https://www.nexusmods.com/stardewvalley/mods/12286?tab=files")
            self.Account.logged = True
        else: #
            print("token is not available")
    
    def get_mod_info(self,GId:int = GameId.STARDEWVALLEY, ModId:int = 0)->Dict:
        data:Dict = {
            "hidden":False
        }
        
        if(not self.Account.logged):
            print("You are not logged")
            return None
        
        URL:str = r"https://www.nexusmods.com/{0}/mods/{1}".format(GameId.Name(GId),ModId)
        print(URL)
        
        res:Response = self.scraper.get(URL)
        bs4 = BeautifulSoup(res.content,"lxml")
        
        #check if mod is hidden
        hidden = bs4.find("h3",id="{0}-title".format(ModId))
        if(hidden != None):
            if(hidden.text.find("Hidden mod") > -1 ):
                data["hidden"] = True
                return data
        
        #get version
        try:
            stat:Tag = bs4.find("li",class_="stat-version").find(class_="stat")
            data["version"] = stat.text
        except:
            res:Response = self.scraper.get(URL)
            bs4 = BeautifulSoup(res.content,"lxml")
            stat:Tag = bs4.find("li",class_="stat-version").find(class_="stat")
            data["version"] = stat.text

        #getFILE iD
        URL = bs4.find(id="action-manual").find("a").attrs["href"]
        
        #url Correction
        if(URL.find("/Core") == 0):
            URL = "https://www.nexusmods.com/{0}".format(URL)
        
        res:Response = self.scraper.get(URL)

        file_id = ""

        if(res.url.find("file_id=") >= 0):
            file_id = res.url.split("file_id=")[1]
        else:
            bs4 = BeautifulSoup(res.content,"lxml")
            idBtn:Tag = bs4.find(class_="btn")
            #tratamento para dd files
            isdd:Tag = bs4.find("dd",class_="clearfix")
            if (not isdd == None):
                tableblock:Tag = bs4.find_all("ul",class_="accordion-downloads")[0]
                url = ""
                #find manual download
                for i in tableblock.find_all("a"):
                    if(str(i.find("span").text).find("Manual download") > -1):
                        url = i.attrs["href"]
                        break

                #url Correction
                if(url.find("/Core") == 0):
                    url = "https://www.nexusmods.com{0}".format(url)
                print(url)
                res = self.scraper.get(url)

                bs4 = BeautifulSoup(res.content,"lxml")
                idBtn:Tag = bs4.find(class_="btn")
                file_id = idBtn.attrs["href"].split("file_id=")[1]
                pass
            else:
                file_id = idBtn.attrs["href"].split("file_id=")[1]
        
        data["file_id"] = file_id
        #downloadLink
        data["download_url"] = self.generate_file_link(file_id,GId)

        return data
    
    def download_file(self, Url:str ,path:Path):
        file = self.scraper.get(Url)
        with open(path,"wb") as f:
            f.write(file.content)
        pass
    
    def generate_file_link(self,file_id:int,game_id:int)->str:
        
        if(not self.Account.logged):
            print("You are not logged")
            return None
        
        URL = r"https://www.nexusmods.com/Core/Libs/Common/Managers/Downloads?GenerateDownloadUrl"
        payload = {
            "fid":file_id,
            "game_id":game_id
        }
        res = self.scraper.post(URL,data=payload).json()
        return res["url"]