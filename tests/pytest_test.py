import urllib2

def test_requests_get():
    req = urllib2.Request('http://data.laastutabloo.ee/api/3/action/package_list')
    response = urllib2.urlopen(req)
    the_page = response.read()
test_requests_get()
