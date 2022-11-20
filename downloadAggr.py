# specify tokeninfo
# download all: list of element, type of query you want to perform
# get token list in a range

import math
from social import Twitter
import pandas as pd
from social import Converter
from price import TokenInfo, CoingeckoScraper
from price import CoingeckoScraper
import threading
import os
from price.coingeckoInfo import TokenInfo

class DownloadAggregator(): 

    def __init__(self, base_directory) -> None:
        self.tokeninfo = pd.read_csv(os.path.join(base_directory, TokenInfo(base_directory).getTokeninfoPath()), index_col='index')
        self.twitter = Twitter(base_directory)
        self.coingecko = CoingeckoScraper(base_directory)


    def downloadTwitter(self, names, query, query_names, start, end, min_likes = 0): 
        for n, qname in zip(names, query_names): 
            if n is None or query_names is None: 
                print('twitter account not existing')
            else: 
                self.twitter.twitterQuery(n, query + qname, start, end, min_likes)

    def downloadListParallel(self, names, query, query_names, start, end, min_likes = 0): 
        step = math.ceil(len(names)/15)
        threads = []
    
        i = 0
        while i < len(names):  
            t = threading.Thread(target=self.downloadTwitter, args=(names[i:i+step],query,query_names[i:i+step], start, end, min_likes))
            t.start()
            threads.append(t)
            i += step

        for t in threads: 
            t.join()

        print('all finished')

    def downloadPrice(self, names, start, end): 
        for n in names: 
            self.coingecko.getPricesFromName(n, start, end)



if "__main__" == __name__: 
    d = DownloadAggregator('data')
    t = TokenInfo('data')
    c = Converter('data')
    names = t.getTokensInRange(155, 159).name.to_list()
    # d.downloadPrice(names,'2021-06-01', '2022-10-01')

    names = [c.nameToTwitterAccount(n) for n in names]
    d.downloadListParallel(names,'',names,'2021-06-01', '2022-10-01', 50)
