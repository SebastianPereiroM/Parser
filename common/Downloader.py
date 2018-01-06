# -*- coding: utf-8 -*-

import requests
import common.DiskCache as DiskCache

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_content(url):

    content = DiskCache.cache[url]
    if content is None:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        page = requests.get(url, verify=False, headers=headers)
        DiskCache.cache[url] = page.text
        content = page.text

    return content






