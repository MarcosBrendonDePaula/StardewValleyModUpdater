from numbers import Number
from typing import Dict
from pyparsing import Path

from requests import Response
from .NexusMods.Nexus import NexusMods
import cloudscraper

class scaping_object_instance(object):
    def __init__(self):
        self.page:Response = ""
        self.scraper:cloudscraper.CloudScraper = cloudscraper.create_scraper("firefox")
    pass

class Mod():
    def __init__(self, args:Dict = {
        "Name":"",
        "Author":"",
        "Version":"",
        "UniqueID":"",
        "MinimumApiVersion":"",
        "UpdateKeys":[""]
    },directory:Path = "/"):
        self.sc_instance:scaping_object_instance = scaping_object_instance()
        self.Name = args.get("Name") or ""
        self.Author = args.get("Author") or ""
        self.Version = args.get("Version") or ""
        self.UniqueID = args.get("UniqueID") or ""
        self.MinimumApiVersion = args.get("MinimumApiVersion") or ""
        self.UpdateKeys:list = args.get("UpdateKeys") or []
        self.Directory:Path = directory
        self.NUKP = -1
        for i in range(len(self.UpdateKeys)):
            if str(self.UpdateKeys[i]).find("Nexus:") != -1:
                token = str(self.UpdateKeys[i]).split(":")[1].split("@")[0]
                if token == "???":
                    self.UpdateKeys[i] = None
                else:
                    self.NUKP = i
                    self.UpdateKeys[i] = token
                return

    def get_page(self):
        if(not self.NUKP == -1):
            self.sc_instance.page = self.sc_instance.scraper.get(self.UpdateKeys[self.NUKP])
            with open("{0}.debug.html".format(self.Name),"w",encoding="utf-8") as output:
                output.write(self.sc_instance.page.content.decode("utf-8"))
        else:
            print("Nexus: not found in the update keys")
        pass

