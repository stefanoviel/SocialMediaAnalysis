import os
import pandas as pd
import re
from price.coingeckoInfo import TokenInfo


class Converter(): 
    def __init__(self, base_directory) -> None:
        self.tokeninfo = pd.read_csv(os.path.join(base_directory, TokenInfo(base_directory).getTokeninfoPath()), index_col='index')

    def nameToTwitterAccount(self, name):
        l = self.tokeninfo.loc[self.tokeninfo.name == name].values.flatten().tolist()
        twitter = [i for i in l if 'twitter' in str(i)]

        if len(twitter) > 0:
            res = re.search('com(.*)', twitter[0])
            return res.group(0)[4:]
        else:
            return None

    def name_symbol(self): 
        pass