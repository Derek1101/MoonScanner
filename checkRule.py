# encoding: utf-8

import requests
import StatusCode


class checkRule(object):
    """description of class"""
    def __init__(self, url):
        self.url = url

    def startCheck(self):
        try:
            response = requests.get(self.url)

            # 1. check for real 404,500 etc
            if response.status_code == StatusCode.StatusCode.OK:
                # 2. check for mooncake 404 or 500 by check redirected url
                if response.url.find('errors/404') > 0:
                    return StatusCode.StatusCode.MoonCake_Not_Found
                elif response.url.find('errors/500') > 0:
                    return StatusCode.StatusCode.MoonCake_Internal_Server_Error
                else:
                    return StatusCode.StatusCode.OK
            else:
                return response.status_code
        except Exception as e:
            return StatusCode.StatusCode.MoonCake_Not_Found


if __name__ == '__main__':
    testUrl = 'http://wacn-ppe.chinacloudsites.cn/zh-cn/documentation/articles/virtual-machines-linux-coreos-how-to'
    badUrl = 'http://wacn-ppe.chinacloudsites.cn/zh-cn/documentation/articles/virtual-machines-choose-me'
    fourUrl = 'http://wacn-ppe.chinacloudsites.cn/documentation/artciles/role-based-access-control-configure'
    imgUrl = 'http://wacnppe.blob.core.chinacloudapi.cn/tech-content/articles/media/virtual-machines-linux-coreos-how-to/cloudservicefromnewportl.png'
    myCheck = checkRule(imgUrl)
    code = myCheck.startCheck()
    print code
