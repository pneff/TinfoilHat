import paranoidlib
import socket
from nose.tools import raises


def test_init():
    h = paranoidlib.Http()
    assert h


def test_allowed_requests():
    # Tests for allowed IPs/hostnames.
    TESTS = [
        # Use port numbers that should not work. This way even if the tests go
        # over the network (I didn't yet mock those parts), it will not do any
        # real requests.
        'http://46.51.189.194:1/',
        'http://www.memonic.com:1/',
        'http://mem.to:1/',
    ]
    for url in TESTS:
        yield check_allowed_requests, url

def check_allowed_requests(url):
    # Test execution for individual tests in test_allowed_requests.
    # Error condition is any unknown raised exception, so there are no asserts.
    # Timeouts and socket errors are ignored as that means the request would
    # have been executed. That will be improved with some stubbing.
    h = paranoidlib.Http(timeout=1)
    try:
        response = h.request(url)
    except AttributeError:
        # That's what httplib2 <=0.6 will raise on timeout
        pass
    except socket.error:
        # That's what httplib2 >0.6 will raise on timeout
        pass


def test_blocked_requests():
    # Tests for blocked IPs/hostnames.
    TESTS = [
        'http://localhost/',
        'http://127.1.1.0/',
        'http://127.0.0.1/',
        # www.local2.ch resolves to 127.0.0.1
        'http://www.local2.ch/',
        'https://www.local2.ch/',
        'http://1.2.3.10/bmi/mashable.com/wp-content/uploads/2010/10/Questions-Answered-Here.jpg',
        'http://192.168.1.2/',
        'http://192.168.10.2/',
        'http://172.16.3.9/',
        'http://0.0.0.0/',
        'https://0.0.0.0/',
        # White space test
        'http://www .memonic.com/',
        # Invalid IP
        'http://256.1.2.3/',
        'http://12.999.2.3/',
    ]
    for url in TESTS:
        yield check_blocked_requests, url

@raises(paranoidlib.BlockedError)
def check_blocked_requests(url):
    # Test execution for individual tests in test_blocked_requests.
    h = paranoidlib.Http(timeout=1, blacklist=["1\.2\.3\.\d+"])
    response = h.request(url)


@raises(paranoidlib.BlockedError)
def test_blocked_twice():
    # Request the same blocked URL twice. This will re-use a connection
    # internally and that used to cause problems.
    h = paranoidlib.Http()
    try:
        h.request('http://0.0.0.0/')
    except paranoidlib.BlockedError:
        pass
    # And again, should raised BlockedError. Used to raise AttributeError.
    h.request('http://0.0.0.0/')
