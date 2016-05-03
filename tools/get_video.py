#!/usr/bin/python

import os
import random
import urllib2
from bs4 import BeautifulSoup

urls = []
sub_str = '/watch?v='
home = 'http://www.youtube.com'
urls.append(home)

while True:
    random.shuffle(urls)
    url = urls.pop()
    print url

    conn = urllib2.urlopen(url)
    html = conn.read()

    soup = BeautifulSoup(html)
    links = soup.find_all('a')

    for tag in links:
        link = tag.get('href', None)
        if link != None:
            if sub_str in link:
                link = home + link
                #print link
                urls.append(link)

    cmd = 'youtube-dl -o \"%(id)s.%(ext)s\" ' + url
    os.system(cmd)


