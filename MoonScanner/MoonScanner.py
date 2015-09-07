#!/usr/bin/env python

import time
import checkRule
import StatusCode
import siteReader
import urllib2
from bs4 import BeautifulSoup

class checker(object):
    def __init__(self):
        # self.urlList = urlList
        self.startStr = '<section class="wa-section">'
        self.endStr = '</section>'
        # wacn host
        self.host = 'http://wacn-ppe.chinacloudsites.cn'
        # url that has been proved good :)
        self.goodSet = set()
        # url that has been proved bad :(
        self.badSet = set()
    def check(self, url):
        # good/bad result
        goodResult = ''
        badResult = ''

        # check for the url given
        firstResult = self.getCheckResult(url, 'Parent Link Error')
        # parent url error
        if not firstResult[0]:
            badResult = badResult + firstResult[1]
        else:
            # open parent url to get page content
            html = urllib2.urlopen(url).read()

            # extract our content between '<section class="wa-section">...</section>'
            siteDict = self.parser(html)

            # Now we got site dictionary in ('url','text'), let's check
            for k, v in siteDict.iteritems():
                result = self.getCheckResult(k,v)
                if result[0]:
                    goodResult = goodResult + result[1]
                else:
                    badResult = badResult + result[1]

        return badResult, goodResult


    def parser(self,html):
        # define temp dict to hold site dictionary
        tempDict = {}
        # extract our content between '<section class="wa-section">...</section>'
        startPos = html.index(self.startStr)
        endPos = html.index(self.endStr, startPos)
        content = html[startPos:endPos]

        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href")
            if href != None:
                # relative link
                if href.strip().startswith('/'):
                    href = self.host + href
                tempDict[href] = link.contents[0]

        return tempDict

    def getCheckResult(self, url, name):
        # CheckResult flag
        flag = True
        # Check result string
        result = '\n %s : %s ' %(name, url)
        # Check if the url is already in our goodSites or badSites
        if url in self.goodSet:
            pass
            # result = result + 'OK\n'
            # return checkFlag, result
        elif url in self.badSet:
            flag = False
        else:
            # New url
            rule = checkRule.checkRule(url)
            status = rule.startCheck()
            # if status good, add to goodSet
            if status == StatusCode.StatusCode.OK:
                self.goodSet.add(url)
            else:
                flag = False
                self.badSet.add(url)

            result += str(status)

        return flag, result

if __name__ == '__main__':
    start = time.clock()
    myReader = siteReader.siteReader('site.txt')
    siteList = myReader.getSiteList()
    count = 0
    goodUrl = badUrl = ''

    myChecker = checker()
    for url in siteList:
        count += 1
        result = myChecker.check(url)
        badUrl += '\n------------------------- Parent Link %d -------------------------\n' %(count)
        goodUrl += '\n------------------------- Parent Link %d -------------------------\n' %(count)
        badUrl += result[0]
        goodUrl += result[1]

    with open('bad.txt','w') as bad:
        bad.write(badUrl.encode('utf-8'))
    with open('good.txt','w') as good:
        good.write(goodUrl.encode('utf-8'))

    print ('All url has been checked, please check out "bad.txt" and "good.txt" for detailed information')
    print (time.clock() - start)