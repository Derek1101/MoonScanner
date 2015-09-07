#!/usr/bin/env python

import checkRule
import StatusCode
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
        # all the urls in one url's content
        siteDict = {}
        # check result
        passCheck = True
        # good/bad result
        goodResult = '\n'
        badResult = '\n'

        # open url to get page content
        html = urllib2.urlopen(url).read()

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
                siteDict[href] = link.contents[0]

        # Now we got site dictionary in ('url','text'), let's check
        for k, v in siteDict.iteritems():
            # Check if the url is already in our goodSites or badSites
            if k in self.goodSet:
                goodResult = v + '\t' + k + '\tOK\n'
                continue
            if k in self.badSet:
                passCheck = False
                badResult = v + '\t' + k + '\tBroken Link' + str(status) +'\n'
                continue
            # New url
            myCheckRule = checkRule.checkRule(k)
            status = myCheckRule.startCheck()
            # if status good, add to goodSet
            if status == StatusCode.StatusCode.OK:
                self.goodSet.add(k)
                goodResult = v + '\t' + k + '\tOK\n'
            else:
                passCheck = False
                self.badSet.add(k)
                badResult = v + '\t' + k + '\tBad Link'+ str(status) +'\n'

        # extract all the link into our innerList
        #with open('OK.txt','w') as good:
        #    good.write(goodResult)
            
        #with open('BAD.txt', 'w') as bad:
        #    bad.write(badResult)

        # Final message
        
        if passCheck:
            return 'Clean page!'
        else:
            print 'Found broken links!'
            return badResult


if __name__ == '__main__':
    myChecker = checker()
    result = myChecker.check('http://wacn-ppe.chinacloudsites.cn/zh-cn/documentation/articles/sql-database-index-advisor')

    print result
    #with open('test.html','w') as html:
    #    html.write(result)