import os
import re
from unicodedata import name
import snscrape.modules.twitter as sntwitter
import datetime
import sys
import pandas as pd
from time import sleep, time
from tqdm import tqdm
import warnings
from manager import Manager


class Twitter(Manager):

    def __init__(self, base_directory: str):
        super().__init__(base_directory, 'twitter')
        warnings.simplefilter(action='ignore', category=FutureWarning)

    def twitterQuery(self, file_name, query, start, end, min_likes=0):
        try:
            df = pd.read_csv(os.path.join(self.directory, file_name), index_col=0)
        except Exception as e:
            print(e)
            df = pd.DataFrame()

        for s, e in self.missing_dates(file_name, start, end, query):
            tweets_list = []
            query1 = query + ' since:' + s + ' until:' + e
            if min_likes > 0:
                query1 = query1 + ' min_faves:' + str(min_likes)

            print('\n[TWITTER] ' + query1)
            disablev = True

            for tweet in tqdm(sntwitter.TwitterSearchScraper(query1).get_items()):

                tweets_list.append(
                    [tweet.date, tweet.id, tweet.user.username, tweet.content, tweet.likeCount, tweet.replyCount,
                     tweet.retweetCount])
            df_new = pd.DataFrame(tweets_list,
                                  columns=['Time', 'Tweet Id', 'Username', 'Text', 'LikeCount', 'ReplyCount', 'Retweet'])
            df_new['Date'] = df_new['Time'].apply(
                lambda x: x.strftime('%Y-%m-%d'))
            # print('old ', len(df), ' new ', len(df_new))
            df = pd.concat([df_new, df])
            # print(len(df))
            df.drop_duplicates(subset=['Tweet Id'])
            df.sort_values(by='Date', inplace=True)
            df.reset_index(drop=True, inplace=True)
            df.to_csv(os.path.join(self.directory, file_name))
            self.update_log()
    
    


if '__main__' == __name__:
    t = Twitter('data')
    t.twitterQuery('SolChicksNFT', "SolChicksNFT", '2022-08-29', '2022-10-03')
