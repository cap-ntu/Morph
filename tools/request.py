import urllib
import urllib2

url = 'http://155.69.52.158/transcoder/get_progress'
key = {'key' : 'G8QKmGXX'}

data = urllib.urlencode(key)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()
print the_page
