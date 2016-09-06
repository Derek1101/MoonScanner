# encoding: utf-8

import time
import multiprocessing as mp
import checkRule
import StatusCode
import siteReader
import urllib2
from bs4 import BeautifulSoup


class Checker(object):
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


def worker(arg, q):
    ''' worker '''
    checker = Checker()
    result = checker.check(arg)
    print('finished')
    return result


def listener(q):
    ''' listen for messages on the q, writes to file. '''
    bad_file = open('bad.md', 'wb')
    good_file = open('good.md', 'wb')

    while True:
        m = q.get()
        if m == 'kill':
            break
        good_result = m[0]
        bad_result = m[1]

        good_file.write(good_result)
        bad_file.write(bad_result)

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
