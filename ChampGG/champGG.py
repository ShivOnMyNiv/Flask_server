# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 21:18:13 2021

@author: derph
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class champGG:
    def __init__(self, champName):
        self.driver = self.initDriver(champName.replace(" ", ""), 1) # source if want to write custom functions
        self.driver2 = self.initDriver(champName.lower(), 2)
        self.champName = champName

     # import from init file
    def initDriver(self, champName, setting):
        if setting == 1:
            # get initial html
            # driverpath = os.path.realpath(r'drivers/chromedriver')
            chrome_options = Options()  
            chrome_options.add_argument("--headless")  
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            # driver = webdriver.Chrome(driverpath, options=chrome_options)
            driver.get('https://champion.gg/champion/' + champName)
        elif setting == 2:
            chrome_options = Options()  
            chrome_options.add_argument("--headless")  
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            # driver = webdriver.Chrome(driverpath, options=chrome_options)
            driver.get('https://www.leagueofgraphs.com/champions/stats/' + champName)
        return driver
    
    def championStats(self):
        champStats = {}
        try:
            champStats["Kills"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[6]/td[2]/p").text.replace(',',''))
            champStats["Deaths"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[7]/td[2]/p").text.replace(',',''))
            champStats["Assists"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[8]/td[2]/p").text.replace(',',''))
            champStats["KDA"] = (champStats["Kills"] + champStats["Assists"]) / champStats["Deaths"]
            DamageDealt = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[9]/td[2]/p").text.replace(',',''))
            champStats["DMG/min"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[3]/div[2]/div/div[4]/div/div[1]/div[2]/div[1]/div").text.replace(',',''))
            time = DamageDealt/champStats["DMG/min"]
            champStats["Gold Earned"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[4]/td[2]/p").text.replace(',',''))
            champStats["CS/min"] = round(float(self.driver2.find_element_by_xpath("/html/body/div[2]/div[3]/div[3]/div[1]/div[2]/div[2]/div[2]/div[6]/div[2]/div/div[1]").text.replace(',',''))/time, 1)
            champStats["averageTime"] = time
        except:
            champStats["Kills"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[6]/td[2]/p").text.replace(',',''))
            champStats["Deaths"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[7]/td[2]/p").text.replace(',',''))
            champStats["Assists"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[8]/td[2]/p").text.replace(',',''))
            champStats["KDA"] = (champStats["Kills"] + champStats["Assists"]) / champStats["Deaths"]
            DamageDealt = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[9]/td[2]/p").text.replace(',',''))
            champStats["DMG/min"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[3]/div[2]/div/div[4]/div/div[1]/div[2]/div[1]/div").text.replace(',',''))
            time = DamageDealt/champStats["DMG/min"]
            champStats["Gold Earned"] = float(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[4]/td[2]/p").text.replace(',',''))
            champStats["CS/min"] = round(float(self.driver2.find_element_by_xpath("/html/body/div[2]/div[3]/div[3]/div[1]/div[2]/div[2]/div[2]/div[6]/div[2]/div/div[1]").text.replace(',',''))/time, 1)
            champStats["averageTime"] = time
        return champStats
    
    def quit(self): 
        self.driver.quit()
        self.driver2.quit()
    
    
    
    
    
    