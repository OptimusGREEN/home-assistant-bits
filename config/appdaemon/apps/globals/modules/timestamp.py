# GLOBAL MODULE

import time
    
def epoch():
    return time.time()

def readable():
    return time.strftime("%d %b %Y %H:%M:%S", time.gmtime())