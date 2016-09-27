# encoding: utf-8

import time
import json
import multiprocessing as mp
from urlparse import urlparse
import requests
import urllib2
import checkRule
import StatusCode
import siteReader
from bs4 import BeautifulSoup


class Checker(object):
    def __init__(self, url):
        # self.urlList = urlList
        self.startStr = '<div class="single-page">'
        self.endStr = '<footer class="footer">'
        self.url = url
        self.json_flag = False
        if self.url.endswith('.json'):
            self.host = 'http://azure.cn'
            self.json_flag = True
        else:
            # wacn host
            parsed_uri = urlparse(url)
            self.host = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        # url that has been proved good :)
        self.goodSet = set()
        # url that has been proved bad :(
        self.badSet = set()

    def check(self):
        # good/bad result
        goodResult = '#### {0}\n'.format(self.url)
        goodResult += '| Name | Link | State |\n'
        goodResult += '| ---- | ---- | ----- |\n'
        badResult = '#### {0}\n'.format(self.url)
        badResult += '| Name | Link | State |\n'
        badResult += '| ---- | ---- | ----- |\n'

        # flag to indicate if error found
        error_flag = False
        # check for the url given
        firstResult = self.getCheckResult(self.url, 'Parent Link Error')
        # parent url error
        if not firstResult[0]:
            badResult = badResult + firstResult[1]
            error_flag = True
            goodResult = ''
        else:
            # open parent url to get page content
            html = urllib2.urlopen(self.url).read()

            # extract our content between '<section class="wa-section">...</section>'
            siteDict = self.json_parser(html) if self.json_flag else self.parser(html)

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
            if not link.contents:
                continue
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


    def json_parser(self, json_html):
        tempDict = {}
        bd = json.loads(json_html)
        nav = bd["navigation"]

        for section in nav:
            articles = section["articles"]
            for article in articles:
                link = article["link"]
                title = article["title"]
                if link.startswith('/'):
                    link = self.host + link

                tempDict[link] = title

        return tempDict

    def getCheckResult(self, url, name):
        # CheckResult flag
        flag = True
        status = 200
        # Check result string
        result = '| {0} | {1} | {2} |\n'
        # Check if the url is already in our goodSites or badSites
        if url in self.badSet:
            flag = False
            # proved to be bad url before
            status = 600
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


def worker(arg, q):
    ''' worker '''
    checker = Checker(arg)
    result = checker.check()
    return result


def listener(q):
    ''' listen for messages on the q, writes to file. '''
    count = 0
    bad_file = open('bad.md', 'wb')
    good_file = open('good.md', 'wb')

    while True:
        m = q.get()
        if m == 'kill':
            break
        bad_result = m[0]
        good_result = m[1]
        bad_file.write(bad_result)
        good_file.write(good_result)
        count += 1
        print('Finish scan {0}'.format(count))

    bad_file.close()
    good_file.close()


if __name__ == '__main__':
    start = time.clock()
    # Use manager queue
    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(mp.cpu_count() + 2)

    # put listener to work first
    watcher = pool.apply_async(listener, (q,))

    myReader = siteReader.siteReader('site.txt')
    siteList = myReader.getSiteList()

    # fire up workers
    jobs = []
    for url in siteList:
        job = pool.apply_async(worker, (url, q))
        jobs.append(job)

    # collect results from the workers throught the pool result queue
    for job in jobs:
        q.put(job.get())

    # now we are done, kill the listener
    q.put('kill')
    pool.close()

    print ('All url has been checked, please check out "bad.md" and "good.md" for detailed info.')
    print ('Total time : {0}'.format(time.clock() - start))
