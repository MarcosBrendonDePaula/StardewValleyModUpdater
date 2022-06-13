import json
from requests import Response, session
from bs4 import BeautifulSoup
import cloudscraper

class JSONCorrect():
    
    @staticmethod
    def Correct(j_text:str = "")->str:
        scrap = cloudscraper.create_scraper("firefox")
        proxies = {"http": "http://localhost:8888", "https": "http://localhost:8888"}
        header = {
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://smapi.io",
            "Referer": "https://smapi.io/json",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }

        body = {
            "SchemaName":"manifest",
            "content": j_text
        }

        res:Response = scrap.post(url="https://smapi.io/json",data=body,headers=header,proxies=proxies, allow_redirects=True)
        res = scrap.get(url=res.url+"/edit")
        bs4 = BeautifulSoup(res.content,"lxml")
        print(bs4.find(id="input").get_text())
        return bs4.find(id="input").get_text()

        pass    