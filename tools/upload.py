import urllib2
import poster.encode
import poster.streaminghttp


opener = poster.streaminghttp.register_openers()

params = {'video_file': open('/home/guanyu/Public/guanyu.mp4','rb'), \
        'target_resolution': '100x100 200x200', \
        'priority': 5}

datagen, headers = poster.encode.multipart_encode(params)
response = opener.open(urllib2.Request('http://155.69.52.158/transcoder/submit_file', datagen, headers))
print response.read()
