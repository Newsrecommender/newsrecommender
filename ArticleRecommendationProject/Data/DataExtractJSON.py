#!/usr/bin/env python2
import json
import os
from collections import defaultdict
import sys  
import pandas as pd

file_path = '/Users/shwetanknagar/Downloads/Personal/Project Eventstreet/Boconni Project/Data Science Project/data'
file_name = os.path.basename('data.json')
path = os.path.join(file_path, file_name)
#print(path)
f = open(path, 'r')
article_list = json.loads(f.read().encode("utf-8"))
print(len(article_list['response']['docs']))
#article_list_df =  pd.DataFrame(article_list['response']['docs'])
