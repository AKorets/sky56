import time
import datetime
import logging
import os
import os.path
from bs4 import BeautifulSoup
from pushbullet import Pushbullet
from selenium import webdriver
import time
import re
patn = re.compile(r'\d{2}-\w{3}-\d{4}')

trackNum = "valid track number" #track number that working on http://www.sky56.cn/english/track/index
pushBulletId = 'valid pushbullet access token' # Access Tokens that you can receive at https://www.pushbullet.com/#settings/account

def getHtmlResponse(trNum):
    driver = webdriver.PhantomJS()

    driver.get('http://www.sky56.cn/english/track/index')
    track_field = driver.find_element_by_id("tracknumbers")  
    track_field.clear()
    track_field.send_keys(trNum)

    clicker =  driver.find_element_by_id("cha")
    clicker.click()

    driver.get('http://www.sky56.cn/track/track/result?tracking_number='+trNum)
 
    response = driver.page_source
    driver.quit()
    return response

def parseHtmlResponse(trNum, htmlResp, fileName):
    res = False
    days = -1
    
    dates = []
    for match in patn.findall(htmlResp):
        try:
            val = datetime.datetime.strptime(match, '%d-%b-%Y')
            dates.append(val)
        except ValueError:
            pass
    now = datetime.datetime.now()
    days = (now-max(dates)).days
    
    if os.path.isfile(fileName):
        with open(fileName, 'r', encoding='utf-8') as content_file:
            content = content_file.read().rstrip('\n')
        if content != htmlResp:
            #print('updated content')
            res = True
    else:
        res = True
    return res,days

def updatePushBullet(days, htmlResp, updatedContent):
    daysStr = "days since last updates "+str(days)	
    if updateExist:
        soup = BeautifulSoup(html,'lxml')
        pb = Pushbullet(pushBulletId)
        for br in soup.find_all("br"):
            br.replace_with("\n")
        push = pb.push_note("Order "+trackNum , daysStr+'\n'+soup.get_text())
    else:
        if days % 5 == 0:
            pb = Pushbullet(pushBulletId)
            push = pb.push_note("Order "+trackNum , daysStr)


fileName = "Track"+trackNum+".txt" 

html = getHtmlResponse(trackNum)

updateExist, days = parseHtmlResponse(trackNum, html, fileName)

updatePushBullet(days, html, updateExist)

if updateExist:
    with open(fileName, "w", encoding='utf-8') as text_file:
        print(html, file=text_file)
