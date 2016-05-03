import urllib
import urllib2



key = {'url': 'http://155.69.52.158/guanyu.mp4',\
       'target_resolution': '100x100 200x200',\
       'priority': 5}

data = urllib.urlencode(key)
req = urllib2.Request('http://155.69.52.158/transcoder/submit_url', data)
response = urllib2.urlopen(req)
the_page = response.read()
print the_page
