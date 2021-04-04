# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 21:35:28 2021

@author: derph
"""

from ChampGG.champGG import champGG
import json

def getStats(name):
    print(name)
    try:
        init = champGG(name)
        stats = init.championStats()
        with open("./ChampGG/" + name + ".json", 'w') as js:
            json.dump(stats, js)
        print(stats)
        init.quit()
    except:
        init = champGG(name)
        stats = init.championStats()                                                                                                                                 
        with open("./ChampGG/" + name + ".json", 'w') as js:
            json.dump(stats, js)
        print(stats)
        init.quit()
"""  
file_precursor = "./DataDragon/"
dataStr = open(file_precursor+"champion.json", encoding="utf8").read()
champNames = list(json.loads(dataStr)["data"].keys())
print(champNames)

run = True
for name in champNames:
    print("\n\n")
    print(name)
    if name == "Zyra":
        run = True
# -*- coding: utf-8 -*-
"""