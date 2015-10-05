import socket
import urllib2
import json

socket.setdefaulttimeout(10)

url="http://mikutter.hachune.net/download/unstable.json?count=1"

response = urllib2.urlopen(url)
json = json.loads(response.read())

print json[0]["version_string"]