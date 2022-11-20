import datetime
import copy
import re
import os
from enum import Enum
from typing import List, Tuple
import json


class Manager:

    def __init__(self, base_directory: str, specific:str):
        self.base_directory = base_directory
        self.directory = os.path.join(base_directory, specific)
        self.log_name = specific + '_log.json'
        f = open(os.path.join(self.base_directory, self.log_name))
        self.log = json.load(f)

    def missing_dates(self, name: str, start: str, end: str, query: str ) -> List[Tuple[str, str]]:
        # query is optional, in case for the same entity I can query data from in different ways

        dates = []

        try: 
            file = next(q for q in self.log[name] if q['query'] == query)
            new_file = copy.deepcopy(file)
        except (StopIteration, KeyError) as e: 
            if type(e).__name__ == 'KeyError': 
                self.log[name] = []
            self.log[name].append({"query":query, "start":start, "end":end})
            return [(start, end)]

        # print(file)

        if start < file['start']:
            new_file['start'] = start
            dates.append((start, file['start']))
            # print('[MANAGER]', start, file['start'])

        if file['end'] < end:
            new_file['end'] = end
            dates.append((file['end'], end))
            # print('[MANAGER]',end, file['end'])

        if file['start'] <= start and file['end'] >= end:
            print('Requirement already satisfied')

        self.log[name].remove(file)
        self.log[name].append(new_file)
        
        # print('dates', dates)
        return dates

    def update_log(self):
        # print(self.log)
        with open(os.path.join(self.base_directory, self.log_name), "w") as outfile:
            outfile.write(json.dumps(self.log, indent=4))


if __name__ == '__main__':
    # print(os.listdir())
    m = Manager('data/twitter')
    print(m.missing_dates('loopringorg', '2022-09-01', '2022-09-30', "from:loopringorg",))
