from zineb.http.request import HTTPRequest
from zineb import signals

request = HTTPRequest('http://example.com')
signals.send(sender='a')
request._send()

print(signals.RECEIVERS)
