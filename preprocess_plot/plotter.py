from cProfile import label
import sys
import datetime
import math
import pandas as pd
import matplotlib.pyplot as plt
import os

sys.path.append(os.path.abspath('.'))
import social
from price.coingeckoInfo import TokenInfo
from preprocess_plot.preprocessing import Preprocess
import matplotlib.dates as mdates
import numpy as np




class Plotter:

    def __init__(self, priceDir, twitterDir, dataDir) -> None:
        self.price_dir = priceDir
        self.twitter_dir = twitterDir
        self.tokeninfo = TokenInfo(dataDir)
        self.c = social.Converter(dataDir)


    def plot(self, preprocessedList:list, plotRawLikes:bool, emas:list) -> None: 
        numElementToPlot = len(preprocessedList)
        
        xn = yn = math.ceil(math.sqrt(numElementToPlot))

        if numElementToPlot < xn*(yn -1 ): 
            yn -= 1

        print(xn, yn)
        if numElementToPlot == 2:
            fig, axs = plt.subplots(2)
        else: 
            fig, axs = plt.subplots(xn, yn)
        fig.set_size_inches(16, 9)
        fig.autofmt_xdate()
        i = 0

        for x in range(xn): 
            for y in range(yn): 
                if i < numElementToPlot: 
                    
                    if numElementToPlot == 1:
                        ax = axs    
                    elif numElementToPlot == 2:
                        ax = axs[i]
                    else: 
                        ax = axs[x, y]
                
                    dates = mdates.date2num(preprocessedList[i][0].Date)
                    
                    if plotRawLikes:
                        print('plotting original likes')
                        ax.plot(dates, preprocessedList[i][0].LikeCount, label='likes')

                    ax.xaxis_date()
                    ax.title.set_text(preprocessedList[i][2] + '_' + preprocessedList[i][3])

                    ax2 = ax.twinx() # create second axs to have different scale
                    ax2.plot(dates, preprocessedList[i][1]['open'].astype('float'), color='red', label='price')

                    # print(emas)
                    for ema in emas: 
                        # print(ema)
                        ax.plot(dates, preprocessedList[i][0].LikeCount.rolling(ema).mean(), label='likes ema '+str(ema))

                    if i == 0: 
                        fig.legend(loc='upper left', prop={'size': 10})
                    
                    i += 1

        plt.show()


if '__main__' == __name__:
    p = Plotter('data/prices', 'data/twitter', 'data')
    pp = Preprocess('data/prices', 'data/twitter', 'data')
    # c = social.Converter('data/tokeninfo.2022-10-04')
    # p.like_price_plot(c.name_account('Solana'), 'Solana', '2022-01-01', '2022-09-01')
    r = pp.preprocessListOfName(['solana', 'okb', 'cronos', 'xrp', 'bitcoin', 'solana','solana','solana','solana','solana'], '2022-01-01', '2022-08-01')
    p.plot(r, False, [10, 30])



    