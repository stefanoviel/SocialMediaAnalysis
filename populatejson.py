import json
import os
import pandas as pd

all = {}

os.chdir('data/twitter')

for f in os.listdir(): 
    print(os.getcwd())
    if f != '_a_log.json': 
        matches = f.split('.')
        os.rename(f, matches[0])
#         all[matches[0]] = [{"query":"from:"+matches[0], "start":matches[1], "end":matches[2]}]

# # Serializing json
# json_object = json.dumps(all, indent=4)
 
# # Writing to sample.json
# with open("_a_log.json", "w") as outfile:
#     outfile.write(json_object) 


# df = pd.read_csv('data/tokeninfo.2022-10-04')
# df.name = df.name.str.lower()
# df.to_csv('data/tokeninfo.2022-10-04', index=False)