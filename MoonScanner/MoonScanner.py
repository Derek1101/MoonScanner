#!/usr/bin/env python

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
        # Parent URL count
        self.count = 0
    def check(self, url):
        # all the urls in one url's content
        siteDict = {}
        # check result
        passCheck = True
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

            # extract all the link into our innerList
            #with open('OK.txt','w') as good:
            #    good.write(goodResult)
            
            #with open('BAD.txt', 'w') as bad:
            #    bad.write(badResult)

            # Final message
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
        checkFlag = True
        # Check result string
        result = '\n'+ name + '\t' + url + '\t'
        # Check if the url is already in our goodSites or badSites
        if url in self.goodSet:
            result = result + 'OK\n'
            # return checkFlag, result
        if url in self.badSet:
            checkFlag = False
            result = result + 'BAD\n'
            
        # New url
        myCheckRule = checkRule.checkRule(url)
        status = myCheckRule.startCheck()
        # if status good, add to goodSet
        if status == StatusCode.StatusCode.OK:
            self.goodSet.add(url)
            result = result + '  ' + str(StatusCode.StatusCode.OK) +'\n'
        else:
            checkFlag = False
            self.badSet.add(url)
            result = result + '  ' + str(status) +'\n'

        return checkFlag, result




if __name__ == '__main__':
    myReader = siteReader.siteReader('site.txt')
    siteList = myReader.getSiteList()
    count = 0
    for url in siteList:
        count += 1
        myChecker = checker()
        result = myChecker.check(url)

        # print "------------------------------BAD LINK-----------------------------------"
        # print result[0]
        # print "------------------------------GOOD LINK----------------------------------"
        # print result[1]
        with open('bad.txt','a') as bad:
            bad.write('------------------------Parent Link - ' + str(count) + '----------------------------')
            bad.write(result[0].encode('utf-8'))
        with open('good.txt','a') as good:
            good.write('------------------------Parent Link - ' + str(count) + '----------------------------')
            good.write(result[1].encode('utf-8'))


    print ('All url has been checked, please check out "bad.txt" and "good.txt" for detailed information')