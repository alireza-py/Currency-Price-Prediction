import requests
import pathlib
import re
from dataclasses import dataclass

@dataclass
class BaseConfigs:
    download = False
    history_directory = pathlib.Path() / 'token-history'

@dataclass
class Token:
    name = None
    interval = None
    interval_daily = "daily"
    interval_weekly = "weekly"
    interval_monthly = "monthly"
    interval_yearly = "yearly"

class Utils:
    def __init__(self) -> None:
        self.internet_connection = True
        if not BaseConfigs.history_directory.exists():
            BaseConfigs.history_directory.mkdir(parents=True, exist_ok=True)

    def download(self, url:str, name:str):
        if not BaseConfigs.download:
            return
        print(f"-> Downloading ({name} file)")
        try:
            response = requests.get(url)
        
            if response.status_code == 200:
                file_loc = BaseConfigs.history_directory / f"{name}.csv"
                with open(file_loc, "wb") as file:
                    file.write(response.content)
                print(f"-> Downloaded ({name} file) \n")
            else:
                print("-> downloading failed\n")
        except:
            print("-> downloading failed\n")
            return -1
    
    def update(self):
        if not BaseConfigs.download:
            return
        for file in self.list_file():
            result = (re.findall(r"\\(.+).csv", str(file)))[0]
            Token.name = result[:-2]
            Token.interval = result[-1]
            name = f"{Token.name}_{Token.interval}"
            print(f"-> Updating ({name} file)")
            try:
                response = requests.get(self.get_main_url())
                if response.status_code == 200:
                    file_loc = BaseConfigs.history_directory / f"{name}.csv"
                    with open(file_loc, "wb") as file:
                        file.write(response.content)
                    print(f"-> Updated ({name} file)")
                else:
                    print("-> Updating failed")
            except:
                print("-> Updating failed")
                return -1

    def check_internet_connection(self):
        try:
            response = requests.get("http://www.google.com", timeout=5)
            response.raise_for_status()
            self.internet_connection = True
            return True
        except (requests.RequestException, requests.Timeout):
            if self.internet_connection:
                print('## Check the internet connection ##')
                self.internet_connection = False
            return False
        
    def get_main_url(self):
        result = f"https://stooq.com/q/d/l/?s={Token.name[:-2]}.v&i={Token.interval}"
        # https://stooq.com/q/d/l/?s=gmt.v&i=m
        return result
    
    def list_file(self) -> tuple:
        result = BaseConfigs.history_directory.glob('*.csv')
        return tuple(result)

    def file_maker(self, name:str):
        file_loc = BaseConfigs.history_directory / f"{name}.csv"
        open(file_loc, "wb")
            
# test = Utils()
# print(test.update())
# for i in test.list_file():
    # print(i)
# if test.check_internet_connection():
#     a = test.download('https://stooq.com/q/d/l/?s=atom.v&i=d', 'atom.v')
