# encoding: utf-8

import time
import checkRule
import StatusCode
import siteReader
import urllib2
from bs4 import BeautifulSoup


class checker(object):
    def __init__(self):
        # self.urlList = urlList
        self.startStr = '<div class="single-page">'
        self.endStr = '<footer class="footer">'
        # wacn host
        self.host = 'https://www.azure.cn'
        # url that has been proved good :)
        self.goodSet = set()
        # url that has been proved bad :(
        self.badSet = set()

    def check(self, url):
        # good/bad result
        goodResult = '#### {0}\n'.format(url)
        goodResult += '| Name | Link | State |\n'
        goodResult += '| ---- | ---- | ----- |\n'
        badResult = '#### {0}\n'.format(url)
        badResult += '| Name | Link | State |\n'
        badResult += '| ---- | ---- | ----- |\n'

        # flag to indicate if error found
        error_flag = False
        # check for the url given
        firstResult = self.getCheckResult(url, 'Parent Link Error')
        # parent url error
        if not firstResult[0]:
            badResult = badResult + firstResult[1]
            error_flag = True
            goodResult = ''
        else:
            # open parent url to get page content
            html = urllib2.urlopen(url).read()

            # extract our content between '<section class="wa-section">...</section>'
            siteDict = self.parser(html)

            # Now we got site dictionary in ('url','text'), let's check
            for k, v in siteDict.iteritems():
                # Inner page link
                result = self.getCheckResult(k, v)
                if result[0]:
                    goodResult = goodResult + result[1]
                else:
                    error_flag = True
                    badResult = badResult + result[1]

        if not error_flag:
            badResult = ''
        return badResult, goodResult

    def parser(self, html):
        # define temp dict to hold site dictionary
        tempDict = {}
        # extract our content between '<section class="wa-section">...</section>'
        startPos = html.index(self.startStr)
        endPos = html.index(self.endStr, startPos)
        content = html[startPos:endPos]

        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href")
            if href is not None:
                # inner link and video link should be skipped
                if href.strip().startswith('#') or \
                        href.strip().startswith('//video') or \
                        href.strip().startswith('mailto:'):
                    continue
                # relative link
                if href.strip().startswith('/'):
                    href = self.host + href
                tempDict[href] = link.contents[0]

        return tempDict

    def getCheckResult(self, url, name):
        # CheckResult flag
        flag = True
        status = 200
        # Check result string
        result = '| {0} | {1} | {2} |\n'
        # Check if the url is already in our goodSites or badSites
        if url not in self.goodSet:
            # New url
            rule = checkRule.checkRule(url)
            status = rule.startCheck()
            # if status good, add to goodSet
            if status == StatusCode.StatusCode.OK:
                self.goodSet.add(url)
            else:
                flag = False
                self.badSet.add(url)

        return flag, result.format(name.encode('utf-8'), url.encode('utf-8'), status)

if __name__ == '__main__':
    start = time.clock()
    myReader = siteReader.siteReader('site.txt')
    siteList = myReader.getSiteList()
    count = 0
    goodUrl = badUrl = ''

    myChecker = checker()
    for url in siteList:
        result = myChecker.check(url)
        badUrl += result[0]
        goodUrl += result[1]
        count += 1
        print(count)

        with open('bad.md', 'w') as bad:
            bad.write(badUrl)
        with open('good.md', 'w') as good:
            good.write(goodUrl)

    print ('All url has been checked, please check out "bad.md" and "good.md" for detailed info.')
    print ('Total time : {0}'.format(time.clock() - start))
