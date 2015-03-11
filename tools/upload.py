import urllib2
import poster.encode
import poster.streaminghttp


opener = poster.streaminghttp.register_openers()

params = {'video_file': open('video.list','rb'), 'target_resolution': '100x100 200x300'}
datagen, headers = poster.encode.multipart_encode(params)
response = opener.open(urllib2.Request('http://155.69.52.158/transcoder/submit', datagen, headers))
print response.read()
