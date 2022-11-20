# preprocess all
# search for certain condition among preprocessed
from cProfile import label
import datetime
import math
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.abspath('.'))
import social
import matplotlib.dates as mdates
import numpy as np
from price import coingeckoInfo

class Preprocess: 

    def __init__(self, priceDir, twitterDir, dataDir) -> None:
        self.tokeninfo = coingeckoInfo.TokenInfo(dataDir)
        self.priceDir = priceDir
        self.twitterDir = twitterDir
        self.c = social.Converter(dataDir)


    def priceLikePreprocessing(self, twitterFile: str, priceFile: str, start: str, end: str) -> None:

        likeDf = pd.read_csv(os.path.join(self.twitterDir, twitterFile))
        price = pd.read_csv(os.path.join(self.priceDir, priceFile))

        # compute like per day
        numberPostsPerDay = likeDf.groupby('Date').size()
        likePerDay = likeDf.groupby('Date')['LikeCount'].sum()/numberPostsPerDay
        likePerDay = likePerDay.to_frame()
        likePerDay = likePerDay.reset_index()
        likePerDay.columns = ['Date', 'LikeCount']

        # get list of dates in the range
        numDays = (datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.datetime.strptime(start, '%Y-%m-%d')).days
        lastDay = datetime.datetime.strptime(end, '%Y-%m-%d')  # .strftime('%Y-%m-%d')
        dateList = [str((lastDay - datetime.timedelta(days=x)).strftime('%Y-%m-%d')) for x in range(numDays + 1)]
        dates = pd.DataFrame(dateList)
        dates.columns = ['Date']
        dates = dates.iloc[::-1]
        dates = dates.reset_index(drop=True)

        # merge price and like database
        priceLikeDf = pd.merge(likePerDay, dates, how='right', on='Date')
        priceLikeDf = pd.merge(priceLikeDf, price, how='left', on='Date')
        priceLikeDf = priceLikeDf.fillna(0)
        priceLikeDf = priceLikeDf.reset_index(drop=True)

        startDateIndex = priceLikeDf.index[priceLikeDf.Date == start].to_list()[0]
        endDateIndex = priceLikeDf.index[priceLikeDf.Date == end].to_list()[0]
        numDays = endDateIndex - startDateIndex

        likeSeries = priceLikeDf[(start < priceLikeDf.Date) & (priceLikeDf.Date < end)]
        priceSeries = priceLikeDf[(start < priceLikeDf.Date) & (priceLikeDf.Date < end)]

        return priceSeries, likeSeries

    def preprocessListOfName(self, name, start, end): 
        ret = []
        for n in name: 
            elem = []
            twit = self.c.nameToTwitterAccount(n)
            if twit is not None: 
                elem.append(self.priceLikePreprocessing(twit, n, start, end)[0])
                elem.append(self.priceLikePreprocessing(twit, n, start, end)[1])
                elem.append(twit)
                elem.append(n)
                ret.append(elem)
            else: 
                print(n, "doesn't have twitter account or it hasn't been downloaded")

        return ret

if '__main__' == __name__:
    p = Preprocess('data/prices', 'data/twitter', 'data')
    # c = social.Converter('data/tokeninfo.2022-10-04')
    # p.like_price_plot(c.name_account('Solana'), 'Solana', '2022-01-01', '2022-09-01')
    r = p.preprocessListOfName(['solana', 'okb', 'cronos', 'xrp', 'bitcoin'], '2022-01-01', '2022-08-01')
    print(r)