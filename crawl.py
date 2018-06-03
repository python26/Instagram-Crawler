
import time
import os
import requests
from utils.browser import Browser
from docopt import docopt

def downloadImage(imageUrl, imagePath):
    img_data = requests.get(imageUrl).content
    with open(imagePath, 'wb') as handler:
        handler.write(img_data)

def writeToFile(filePath, data):
    file = open(filePath, 'w', encoding='utf8')
    for i in data:
        if type(i) is list:
            i = "\n".join(i)
        file.write(str(i)+"\n")
    file.close()

def makeDir(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    else:
        if len(os.listdir(dirPath)) == 3:
            return False
    return True

def extractLikes(data):
    result = ""
    try:
        result = data[1][:-2]
    except Exception as e:
        print("No like data")
        result = ""
    return result

def extractComments(data):
    result = ""
    try:
        result = data[3][:-1]
    except Exception as e:
        print("No comment data")
        result = ""
    return result

def extractDateTime(data):
    result = ""
    try:
        result = data.split('datetime="')[1].split('"')[0]
    except Exception as e:
        print("No dateTime data")
        result = ""
    return result

def extractCommentsMessage(data):
    results = []
    try:
        sp = data.split("FPmhX notranslate TlrDj")
        if len(sp) > 2:
            for i in range(len(sp)):
                if i > 1:
                    name = sp[i].split(">")[1].split("<")[0]
                    message = sp[i].split(">")[3].split("<")[0]
                    results.append(name+": "+message)
    except Exception as e:
        print("No CommentsMessage data")
        results = []
    return results

def extractMessage(data):
    result = ""
    try:
        splitData = data.split('<img alt="')
        if len(splitData) > 1:
            result = splitData[1].split('"')[0]
        else:
            # only english?
            result = data.split('{"node":{"text":"')[1].split('"}')[0]
            result = result.encode('utf-8').decode('unicode-escape')
            print(result)
    except Exception as e:
        print("No message data")
        result = ""
    return result

def runCrawl(limitNum = 0,queryList = []):
    browser = Browser("driver/chromedriver")
    for query in queryList:
        browser.clearLink()
        makeDir("data")
        makeDir("data/"+query)
        mUrl = ""
        if query[0] == "#":
            mUrl = "https://www.instagram.com/explore/tags/"+query[1:]
        else:
            mUrl = "https://www.instagram.com/"+query
        browser.goToPage(mUrl)
        print("collecting url of " + query + "...")
        browser.scrollPageToBottomUntilEnd(browser.collectDpageUrl, limitNum)
        print("finish scoll collecting!")

        print("collecting data...")
        slist = list(set(browser.urlList))
        for url in slist:
            dirName = url.split("/")[4]
            # skip if already crawled 
            if not makeDir("data/"+query+"/"+dirName):
                continue
            browser.goToPage(url)
            cur = browser.getPageSource()
            writeToFile("data/"+query+"/"+dirName+"/raw.html", [cur])
            infoData = cur.split("<meta content=")[1].split(" ")
            # extract data
            likes = extractLikes(infoData)
            comments = extractComments(infoData)
            message = extractMessage(cur)
            dateTime = extractDateTime(cur)
            commentMessages = extractCommentsMessage(cur)
            print("likes:",likes," comments:", comments," message:", message, 
                "commentMessages:", commentMessages, "dateTime:", dateTime)
            writeToFile(
                "data/"+query+"/"+dirName+"/info.txt", 
                [   
                    "likes: ", likes, "",
                    "comments: ", comments, "",
                    "message: ", message, "",
                    "commentMessages: ", commentMessages, "",
                    "dateTime: ", dateTime, ""
                ]
            )
            # download image
            imageUrl = cur.split('meta property="og:image" content="')[1].split('"')[0]
            downloadImage(imageUrl,"data/"+query+"/"+dirName+"/image.jpg")
            time.sleep(1)
        print("query " + query + " collecting finish")

    time.sleep(2)
    browser.driver.quit()
    print("FINISH!")

def main():
    args = docopt("""
    Usage:
        crawl.py [-q QUERY] [-n NUMBER] [-h HELP]
    
    Options:
        -q QUERY  username, add '#' to search for hashtags, e.g. 'username' or '#hashtag'
                  For multiple query seperate with comma, e.g. 'username1, username2, #hashtag'

        -n NUM    number of returned posts [default: 10000]

        -h HELP   show this help message and exit
    """)

    limitNum = int(args.get('-n', 10000))
    query = args.get('-q', "")
    if not query:
        print('Please input query!')
    else:
        queryList = query.replace(" ","").split(",")
        runCrawl(limitNum=limitNum, queryList=queryList)

main()


            
            
            
            
            
            
            
            
            
            
            
            
            

            
            
            
            