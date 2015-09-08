## MoonScanner
**MoonScanner** is a scan tool which could scann all the links (site, image, inner link) and generate broken link and good link report.

## Support for
+ check broken link 
+ generate both good link and bad link report

## How to 
1. Please install **beautifulsoup4** first using:
```python
	pip install beautifulsoup4
```
2. then run the command below
```python
	python MoonScanner.py
```
then you will have two reports: good.txt and bad.txt, check detail link information on it.
the report format will be : link-name : link-url status

## How it works?
Supporsed the given link is **http://wacn.ppe.chinaclouds.cn/documentation/articles/virtual-machine-deploy**
1. Check for given link's accessiblity, if it's broken, write it in broken link's report (bad.txt); if good, goto **2**
2. Get all the html elements in the given page, then extract the main-part, abadon header&footer link.
3. Get all the links <a>(currently only a, but image support should be easy), and get their "href" and "text", filter None link which has no "href" proprety.
4. Check every link, if it is in **good link list** or **bad link list**, there is no need to check it, just generate its result. If it's new url, check its
status code, if good link, add to global **good link list**, bad link otherwise.
5. At last, write bad link and good link into each file as report.

## Issue
+ Inner link support, such as 'http://wacn.ppe.chinaclouds.cn/documentation/articles/virtual-machine-deploy#Step2', currently we just ignore inner link, but it should proivde better solution to this.
+ Performance is not fast as imagined, I've test 3 sites, average time for check one page is about 6s~10s.

## TODO
+ More links formats support should be add:
	- inner link (should provide better solution)
	- etc.
+ Speed up our program by using **multi-threading** ??
