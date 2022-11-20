from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text, HTML
import pprint
import json
from tabulate import tabulate
import os
from prompt_toolkit.completion import WordCompleter
import ast
from prompt_toolkit import prompt
from social import Twitter
from social import Converter
from prompt_toolkit.completion import NestedCompleter
from price import TokenInfo, CoingeckoScraper
from downloadAggr import DownloadAggregator
from preprocess_plot import plotter, preprocessing
import pandas as pd
import pprint

dataDir = 'data'
twitterDir = 'data/twitter'
priceDir = 'data/prices'

class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Command:
    def __init__(self, name, nparameters, func, help, *digits) -> None:
        self.name = name
        self.nparameters = nparameters
        self.help = help
        self.func = func
        self.digits = digits

    def checkParametersExecute(self, args):
        if self.name == args[0]:
            show = save = False

            if '-h' in args:
                print(self.help)

            
            elif self.nparameters == len(args):
                parameters = []
                i = 0
                for n, a in enumerate(args):
                    if len(self.digits) > 0 and n == self.digits[i]:
                        parameters.append(int(a))
                        i += 1
                    else:
                        parameters.append(a)

                res = self.func(*parameters[1:])
                if res is not None: 
                    print(res)

            else: 
                print(self.nparameters, len(args))
                print('[ERR] wrong number of arguments check', self.name, '-h for more information' )
    

            


class Cmd:
    def __init__(self) -> None:
        self.preproc = preprocessing.Preprocess(priceDir, twitterDir, dataDir)
        self.plotter = plotter.Plotter(priceDir, twitterDir, dataDir)
        self.tokeninfo = TokenInfo(dataDir)
        self.tokeninfoDB = pd.read_csv(os.path.join(self.tokeninfo.data_directory, self.tokeninfo.getTokeninfoPath()), index_col='index')
        self.coingecko = CoingeckoScraper(dataDir)
        self.aggregate_downloader = DownloadAggregator(dataDir)
        self.converter = Converter(dataDir)
        self.twitter = Twitter(dataDir)
        self.commandlist = []
        self.resetSaved()
        self.commandsdict = {}
        
        help = """\ncommand: update-tokenlist [digit]\n
        Download token list from coingecko with relative informations,
        [digit] is the number of pages to be downloaded where 1 page 
        corresponds to 100 tokens"""
        self.addCommandToCmdList('download-tokenlist', 2, self.tokeninfo.downloadTokenlist,
                    help, 1)

        help = """\ncommand: get-range [digit] [digit]\n
        Gets tokens in a certain range from tokenlist"""
        self.addCommandToCmdList('get-range', 3, self.getTokensInRange, help, 1, 2)

        help = """\ncommand: get-similar [str]\n
        Gets tokens containing substring [str]"""
        self.addCommandToCmdList('get-similar', 2, self.getSimilarTokens,
                    help)

        help = """\ncommand: print-saved\n
        Print list currently saved in memory"""
        self.addCommandToCmdList('print-saved', 1, self.print_saved, help)

        help = """\ncommand: print-commands\n
        Print availible commands"""
        self.addCommandToCmdList('print-commands', 1, self.print_commands, help)

        help = """\ncommand: preproc [date:str] [date:str]\n
        preprocess saved list of tokens to plot"""
        self.addCommandToCmdList('preproc', 3, self.preprocessList, help)

        help = """\ncommand: download-price\n
        scrape daily price of tokens currently in memory from Coingecko 
        since listing of the coin until today"""
        self.addCommandToCmdList('download-price', 1, self.downloadListOfNames, help)

        help = f"""\ncommand: print-multiplot [plotRawLikes:bool] [emas:list]\n
        IMPORTANT: [emas:list] should be given withouth spaces
        plot saved preprocessed tokens """
        self.addCommandToCmdList('print-multiplot', 3, self.multiPlot, help)

        help = f"""\ncommand: download-twitter [query:str] [minlikes:int] [date:str] [date:str]\n
        scrape daily price of accounts currently in memory from Twitter"""
        self.addCommandToCmdList('download-twitter', 5, self.dowloadListTwitter, help)

        help = f"""\ncommand: reset-saved\n
        reset temporaly saved data"""
        self.addCommandToCmdList('reset-saved', 1, self.resetSaved, help)

        help = f"""\ncommand: twitter-query [file_name: str] [query:str] [minlikes:int], [start:int], [end:int] \n
        make specific twitter query"""
        self.addCommandToCmdList('twitter-query', 6, self.singleQuery, help)

        help = f"""\ncommand: print-account-name\n
        print name of twitter account given the name of the token"""
        self.addCommandToCmdList('print-account-name', 1, self.printAccountsName , help)

        help = f"""\ncommand: check-availibity\n
        print name of twitter account given the name of the token"""
        self.addCommandToCmdList('check-availibity', 1, self.checkAvailibility , help)


    def main(self):
        session = PromptSession()
        completer = NestedCompleter.from_nested_dict(self.commandsdict)

        while True:
            try:
                text = prompt('> ', completer=completer)
            except KeyboardInterrupt:
                print('Press [CTRL+D] to exit')
                continue
            except EOFError:
                break
            else:
                args = text.split(' ')
                for c in self.commandlist:
                    try:
                        c.checkParametersExecute(args)
                    except FileNotFoundError as e: 
                        print('expeptino', e)


        print('Exiting..')

    def addCommandToCmdList(self, name, nparameters, func, help='', *digits):
        c = Command(name, nparameters, func, help, *digits)
        self.commandsdict[c.name] = None
        self.commandlist.append(c)

    def print_saved(self): 
        print(self.df)

    def print_commands(self): 
        print()
        for c in self.commandlist: 
            print( f"\n*{Bcolors.OKBLUE}",c.name, f'{Bcolors.ENDC}', c.help)
        print()
            
    def preprocessList(self, start, end): 
        print('preprocessing')
        if self.df is None or len(self.df) == 0: 
            print('[ERR] No list of elements in memory')
        else: 
            name = self.df.name.to_list()
            self.df = self.preproc.preprocessListOfName(name, start, end)
            return self.df

    def downloadListOfNames(self): 
        return self.coingecko.getPricesFromListNames(self.df.name.to_list())

    def multiPlot(self, plotRawLikes, emas): 
        self.plotter.plot(self.df, ast.literal_eval(plotRawLikes), ast.literal_eval(emas))

    def dowloadListTwitter(self, query, minlikes, start, end): 
        names = [self.converter.nameToTwitterAccount(n) for n in self.df.name.to_list()]
        # self.aggregate_downloader.downloadListParallel(names, '',names, start, end)
        if query == "''": 
            print('here')
            self.aggregate_downloader.downloadListParallel(names, '', names, start, end,  int(minlikes))
        else: 
            self.aggregate_downloader.downloadListParallel(names, query, names, start, end, int(minlikes)) #TODO try this

    def singleQuery(self, file_name, query, minlikes, start, end): 
        self.twitter.twitterQuery(file_name, query, start, end, int(minlikes))

    def resetSaved(self): 
        self.df = self.tokeninfoDB

    def printAccountsName(self): 
        for n, elem in enumerate([self.converter.nameToTwitterAccount(n) for n in self.df.name.to_list()]): 
            print(n, '-', elem)
        
    def getTokensInRange(self, start, end): 
        self.df = self.tokeninfo.getTokensInRange(self.df, start, end)
        self.df.reset_index(inplace=True, drop=True)
        return self.df


    def getSimilarTokens(self, name): 
        self.df = self.tokeninfo.getSimilarTokens(self.df, name)
        self.df.reset_index(inplace=True, drop=True)
        return self.df

    def checkAvailibility(self):
        existenceTable = []
        for n in self.df.name.to_list(): 
            # priceExists = os.path.exists(os.path.join(dataDir, 'prices', n))
            # twitterExists = os.path.exists(os.path.join(dataDir, 'twitter', ))
            f = open('data/twitter_log.json')
            jsonTwitter = json.load(f)
            twitterName = self.converter.nameToTwitterAccount(n)
            

            f = open('data/prices_log.json')
            jsonPrice = json.load(f)
            print(n)

            print('   * Twitter:')
            try: 
                print(jsonTwitter[twitterName][0])
            except KeyError: 
                print('File not availible, please download with download-twitter/twitter-query')

            print('   * Price:')
            try: 
                print(jsonPrice[n][0])
            except: 
                print('File not availible, please download with download-price')
        


if __name__ == '__main__':
    c = Cmd()

    # help = """\ncommand: preprocess-list [str]\n
    # Gets tokens containing substring [str"""
    # c.add_command('get-similar', 2, tokeninfo.get_similar,
    #               help)

    c.main()

