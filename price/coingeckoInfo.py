from bs4 import BeautifulSoup
import requests
import time
from tqdm import tqdm
import datetime
import cloudscraper
import pandas as pd
import os


class TokenInfo:

    def __init__(self, data_directory) -> None:
        self.data_directory = data_directory

    def downloadTokenlist(self, num: int):
        """
        Saves tokenlist downloaded from coingecko in data folder under tokeinfo.date

        :param num: number of tokens to scrape
        :return: list of tokens (name, specific webpage)
        """

        db = []
        print('downloading list')
        for i in tqdm(range(1, num + 1)):
            URL = "https://www.coingecko.com/?page=" + str(i)
            scraper = cloudscraper.create_scraper(
                delay=5,   browser={'custom': 'ScraperBot/1.0', })
            r = scraper.get(URL)
            soup = BeautifulSoup(r.content, 'html.parser')

            # , attrs={"rel": "nofollow noopener"})
            items = soup.find_all(
                "a", class_="tw-flex tw-items-start md:tw-flex-row tw-flex-col")

            for i in items:
                elem = [i.find_all("span", class_="lg:tw-flex font-bold tw-items-center tw-justify-between")[0].text.strip(), 
                i.find_all("span", class_="d-lg-inline font-normal text-3xs tw-ml-0 md:tw-ml-2 md:tw-self-center tw-text-gray-500 dark:tw-text-white dark:tw-text-opacity-60")[0].text.strip(),
                i['href']]

                elem[0] = elem[0].replace('/', '') # to not compromise name of file
                # print(elem)
                db.append(elem)

        df = pd.DataFrame(db)
        # print(df)
        df.columns = ['name', 'symbol', 'url']
        df.name = df.name.str.lower()

        links = []
        s = time.time()
        print('downloading details')
        for index, row in tqdm(df.iterrows()):
            scraper = cloudscraper.create_scraper(
                delay=1,   browser={'custom': 'ScraperBot/1.0', })
            r = scraper.get('https://www.coingecko.com' + row['url'])

            soup = BeautifulSoup(r.content, 'html.parser')
            res = soup.find_all('a',
                                class_="tw-px-2.5 tw-py-1 tw-my-0.5 tw-mr-1 tw-rounded-md tw-text-sm tw-font-medium tw-bg-gray-100 tw-text-gray-800 hover:tw-bg-gray-200 dark:tw-text-white dark:tw-bg-white dark:tw-bg-opacity-10 dark:hover:tw-bg-opacity-20 dark:focus:tw-bg-opacity-20")
            links.append([i['href'] for i in res])

        links = pd.DataFrame(links)
        # remove previous token list
        os.remove(os.path.join(self.data_directory, self.getTokeninfoPath()))
        df_concat = pd.concat([df, links], axis=1)
        df_concat.to_csv(self.data_directory + '/tokeninfo.' + datetime.datetime.today().strftime('%Y-%m-%d'), index_label='index')
        # print(time.time() - s)

    def getTokeninfoPath(self): 
        matches = [i for i in os.listdir(self.data_directory) if 'tokeninfo' in i]
        if len (matches) != 1: 
            print('matches: ', matches)
            raise Exception('[ERR] tokeinfo not unique')
        
        return matches[0]


    def getTokensInRange(self, df, start, end): 
        # tokeninfo = pd.read_csv(os.path.join(self.data_directory, self.getTokeninfoPath()), index_col='index')
        return df.iloc[start:end]

    def getSimilarTokens(self, df, name): 
        # tokeninfo = pd.read_csv(os.path.join(self.data_directory, self.getTokeninfoPath()), index_col='index')
        return df.loc[df.name.str.contains(name)]

if __name__ == "__main__":
    c = TokenInfo('data')
    c.downloadTokenlist(21)
    