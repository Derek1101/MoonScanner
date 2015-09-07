class siteReader(object):
    """description of class"""
    def __init__(self, filePath):
        self.filePath = filePath
        self.siteList = []

    def getSiteList(self):
        with open(self.filePath, 'r') as sites:
            for line in sites.readlines():
                self.siteList.append(line.strip())
        return self.siteList


if __name__ == '__main__':
    reader = siteReader('site.txt')
    print reader.getSiteList()


