'''Module for parsing Jupyter tracebacks'''

import pickle
import os

BADWORDSPATH = os.path.abspath(__file__).replace('Parser.py', 
    'static/main/codes.pkl')

def __getcodes__():
    with open(BADWORDSPATH, 'rb') as f:
        return pickle.load(f)
    
codes = __getcodes__()

def parse(traceback):
    for i in codes:
        traceback = traceback.replace(i, '')
    return traceback

def addbadword(badword):
    global codes
    codes.append(badword)
    with open(BADWORDSPATH, 'wb') as f:
        pickle.dump(codes, f)
        
def removebadword(badword):
    global codes
    codes.remove(badword)
    with open(BADWORDSPATH, 'wb') as f:
        pickle.dump(codes, f)
