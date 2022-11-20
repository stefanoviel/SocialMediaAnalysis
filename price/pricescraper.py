from dataclasses import dataclass
from email.mime import base
import os
import requests
import datetime
import pandas as pd
import json
from bs4 import BeautifulSoup
import cloudscraper
import cloudscraper
from enum import Enum
import sys
sys.path.append(os.path.abspath('.'))
from manager import Manager
from price import TokenInfo


class CoingeckoScraper(Manager):

    def __init__(self, base_directory: str):
        super().__init__(base_directory, 'prices')
        self.t = TokenInfo(self.base_directory)
        self.tokeinfo = pd.read_csv(os.path.join(base_directory, self.t.getTokeninfoPath()))

    def getPricesFromName(self, name, start, end):
        # print(self.directory, name)
        try:
            SavedDf = pd.read_csv(os.path.join(
                self.directory, name), index_col=0)
        except FileNotFoundError as e:
            # print(e)
            SavedDf = pd.DataFrame()

        for s, e in self.missing_dates(name, start, end, name):
            print('[COINGECKO] Scraping klines ' + name + ' from ', s, 'to', e)
            url = self.tokeinfo.loc[self.tokeinfo.name == name].url.iloc[0]
            scraper = cloudscraper.create_scraper(
                delay=5,   browser={'custom': 'ScraperBot/1.0', })
            r = scraper.get('https://www.coingecko.com' + url)
            
            soup = BeautifulSoup(r.content, 'html.parser')

            baseCssClass = "tw-bg-white dark:tw-bg-white dark:tw-bg-opacity-5 dark:tw-text-white tw-h-8 tw--ml-px tw-relative " \
                "tw-inline-flex tw-items-center tw-px-4 tw-py-2 tw-border-solid tw-border tw-cursor-pointer " \
                "tw-border-gray-300 tw-text-sm tw-font-medium tw-text-gray-700 hover:tw-bg-gray-50 " \
                "dark:hover:tw-bg-opacity-10 focus:tw-z-10 focus:tw-outline-none focus:tw-bg-gray-200 " \
                "dark:tw-border-opacity-10 dark:focus:tw-bg-opacity-10 dark:hover:tw-text-white graph-stats-btn-"


            startDate = datetime.datetime.strptime(s, '%Y-%m-%d')

            if (datetime.datetime.today() - startDate).days < 30:
                res = soup.find_all('a',
                                    class_=baseCssClass + '30d')
            elif (datetime.datetime.today() - startDate).days < 90:
                res = soup.find_all('a',
                                    class_=baseCssClass + '90d')
            elif (datetime.datetime.today() - startDate).days < 180:
                res = soup.find_all('a',
                                    class_="tw-bg-white dark:tw-bg-white dark:tw-bg-opacity-5 dark:tw-text-white tw-h-8 tw--ml-px tw-relative tw-inline-flex tw-items-center tw-px-4 tw-py-2 tw-border-solid tw-border tw-cursor-pointer tw-border-gray-300 tw-text-sm tw-font-medium tw-text-gray-700 hover:tw-bg-gray-50 dark:hover:tw-bg-opacity-10 focus:tw-z-10 focus:tw-outline-none focus:tw-bg-gray-200 dark:tw-border-opacity-10 dark:focus:tw-bg-opacity-10 dark:hover:tw-text-white graph-stats-btn graph-stats-btn-180d tw-hidden md:tw-flex")
            elif (datetime.datetime.today() - startDate).days < 365:
                res = soup.find_all('a',
                                    class_="tw-bg-white dark:tw-bg-white dark:tw-bg-opacity-5 dark:tw-text-white tw-h-8 tw--ml-px tw-relative tw-inline-flex tw-items-center tw-px-4 tw-py-2 tw-border-solid tw-border tw-cursor-pointer tw-border-gray-300 tw-text-sm tw-font-medium tw-text-gray-700 hover:tw-bg-gray-50 dark:hover:tw-bg-opacity-10 focus:tw-z-10 focus:tw-outline-none focus:tw-bg-gray-200 dark:tw-border-opacity-10 dark:focus:tw-bg-opacity-10 dark:hover:tw-text-white graph-stats-btn graph-stats-btn-1y tw-hidden md:tw-flex")
            else:
                res = soup.find_all('a',
                                    class_="tw-bg-white dark:tw-bg-white dark:tw-bg-opacity-5 dark:tw-text-white tw-h-8 tw--ml-px tw-relative tw-inline-flex tw-items-center tw-px-4 tw-py-2 tw-rounded-r-md tw-border-solid tw-border tw-cursor-pointer tw-border-gray-300 tw-text-sm tw-font-medium tw-text-gray-700 hover:tw-bg-gray-50 dark:hover:tw-bg-opacity-10 focus:tw-z-10 focus:tw-outline-none focus:tw-bg-gray-200 dark:tw-border-opacity-10 dark:focus:tw-bg-opacity-10 dark:hover:tw-text-white graph-stats-btn graph-stats-btn-max")

            url = res[0]['data-graph-stats-url']
            r = scraper.get(url).text
            data = json.loads(r)
            priceDf = pd.DataFrame(data['stats'])
            priceDf.columns = ['Time', 'open']
            
            url = url.replace('price_charts', 'market_cap')
            r = scraper.get(url).text
            data = json.loads(r)
            mktcapDf = pd.DataFrame(data['stats'])
            mktcapDf.columns = ['Time', 'mktcap']

            # print(SavedDf)
            if SavedDf.empty: 
                SavedDf = pd.merge(priceDf, mktcapDf, on='Time')
            else: 
                SavedDf = pd.concat([pd.merge(priceDf, mktcapDf, on='Time'), SavedDf])
            SavedDf.drop_duplicates(subset=['Time'])
            # print(pd.merge(priceDf, mktcapDf, on='Time'))
            # print(SavedDf)
            SavedDf['Date'] = SavedDf['Time'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d'))
            SavedDf.to_csv(os.path.join(self.directory, name))
            self.update_log()


    def getPricesFromListNames(self, names): 
        for n in names: 
            self.getPricesFromName(n, '2008-01-01', datetime.datetime.today().strftime('%Y-%m-%d'))




if __name__ == "__main__":
    c = CoingeckoScraper('data')
    c.getPricesFromName('uniswap', '2019-12-10', '2022-10-01')