"""
httplib2 extension that is more paranoid about input.
"""
__version__ = "0.3"
__author__ = [
    "Patrice Neff <mail@patrice.ch>",
]


import httplib2
import socket
import re

try:
    import socks
except ImportError:
    socks = None

# Regular expression that matches all the blocked IPs
BLOCKRE = re.compile(r"""
    (
      0\.\d{0,3}\.\d{0,3}\.\d{0,3}    # 0.0.0.0/8
    | 10\.\d{0,3}\.\d{0,3}\.\d{0,3}   # 10.0.0.0/8
    | 127\.\d{0,3}\.\d{0,3}\.\d{0,3}  # 127.0.0.0/8
    | 172\.16\.\d{0,3}\.\d{0,3}       # 127.16.0.0/12
    | 169\.254\.\d{0,3}\.\d{0,3}      # 169.254.0.0/16
    | 192\.168\.\d{0,3}\.\d{0,3}      # 192.168.0.0/16
    | 192\.0\.2\.\d{0,3}              # 192.0.2.0/24
    | 192\.88\.99\.\d{0,3}            # 192.88.99.0/24
    | 255\.255\.255\.255              # 255.255.255.255
    # multicast: 224.0.0.0 - 239.255.255.255
    # http://www.iana.org/assignments/multicast-addresses/multicast-addresses.xml
    | 22[4-9]\.\d{0,3}\.\d{0,3}\.\d{0,3}
    | 23[0-9]\.\d{0,3}\.\d{0,3}\.\d{0,3}
    # Any whitespace is suspicious
    | .*\s.*
    # Hostname that doesn't need to be resolved
    | localhost
    )
    """, re.VERBOSE).match

# Matches IP-like strings
IS_IP = re.compile('\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}').match

# Default request timeout in seconds
DEFAULT_TIMEOUT = 10


class BlockedError(Exception):
    """Exception raised when a request was blocked."""


class UnsupportedError(Exception):
    """Raised when the socket family is not supported (currently this library
    only works for IPv4 addresses).
    """


def is_blocked(ip, blacklist):
    """Checks if the given IP is blocked."""
    ip = ip.strip()
    if BLOCKRE(ip):
        return True

    # Test for valid IP
    if IS_IP(ip):
        parts = ip.split('.')
        for p in parts:
            if int(p) > 255:
                # Invalid IP
                return True

    if blacklist:
        for b in blacklist:
            if b and re.match(b, ip):
                return True
    return False


def is_blocked_sockaddr(family, sockaddr, blacklist):
    """Checks if a socket address is blocked."""
    if family not in (socket.AF_INET, socket.AF_INET6):
        raise UnsupportedError("Unsupported address family %d" % family)
    ip = sockaddr[0]
    return is_blocked(ip, blacklist=blacklist)


class HTTPConnection(httplib2.HTTPConnectionWithTimeout):
    def connect(self):
        """Connect to the host and port specified in __init__."""
        # Unfortunately 99% of this method have been copied directly from
        # httplib2. It does not have any good hooks for inserting our
        # functions.

        # Different from httplib2 (blocking)
        if is_blocked(self.host, blacklist=self.blacklist):
            raise BlockedError("Host name %s is blocked" % self.host)
        # Again the same as httplib2 from here

        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(self.host, self.port, 0,
                socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            # Different from httplib2 (blocking)
            if is_blocked_sockaddr(af, sa, blacklist=self.blacklist):
                raise BlockedError("Host name %s is blocked" % self.host)
            # Again the same as httplib2 from here
            try:
                if self.proxy_info and self.proxy_info.isgood():
                    self.sock = socks.socksocket(af, socktype, proto)
                    self.sock.setproxy(*self.proxy_info.astuple())
                else:
                    self.sock = socket.socket(af, socktype, proto)
                if httplib2.has_timeout(self.timeout):
                    self.sock.settimeout(self.timeout)
                if self.debuglevel > 0:
                    print "connect: (%s, %s)" % (self.host, self.port)

                self.sock.connect(sa)
            except socket.error, msg:
                if self.debuglevel > 0:
                    print 'connect fail:', (self.host, self.port)
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg


class HTTPSConnection(httplib2.HTTPSConnectionWithTimeout):
    def connect(self):
        """
        The HTTPSConnectionWithTimeout class does very little - among others it
        does not manually execute the getaddrinfo calls. To avoid writing the
        whole class in a new way, this function just checks the hostname and
        then loads off to the parent class. The main disadvantages of that are
        that DNS resolving is done twice (though as it's well cached that
        shouldn't be an issue) and more seriously that the second resolving
        just might return a different IP address - especially if it's a
        carefully executed attack.
        """

        if is_blocked(self.host, blacklist=self.blacklist):
            raise BlockedError("Host name %s is blocked" % self.host)

        for res in socket.getaddrinfo(self.host, self.port, 0,
                socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            if is_blocked_sockaddr(af, sa, blacklist=self.blacklist):
                raise BlockedError("Host name %s is blocked" % self.host)

        return httplib2.HTTPSConnectionWithTimeout.connect(self)


class Http(httplib2.Http):
    def __init__(self, cache=None, timeout=DEFAULT_TIMEOUT, proxy_info=None,
                 blacklist=None):
        self.blacklist = blacklist
        return httplib2.Http.__init__(self, cache=cache, timeout=timeout,
                                      proxy_info=proxy_info)

    def request(self, uri, method="GET", body=None, headers=None,
                redirections=httplib2.DEFAULT_MAX_REDIRECTS):
        (scheme, authority, request_uri, defrag_uri) = httplib2.urlnorm(uri)
        connection_type = (scheme == 'https') and HTTPSConnection or HTTPConnection
        return httplib2.Http.request(self, uri, method, body, headers,
                                     redirections, connection_type)

    def _request(self, conn, host, absolute_uri, request_uri, method, body,
                 headers, redirections, cachekey):
        # Until this moment nothing has been done on the connection, so we can
        # safely add the required parameters here.
        # Better would have been to do it right at construction time, but
        # httplib2 doesn't have good hooks for that.
        conn.blacklist = self.blacklist
        return httplib2.Http._request(self, conn, host, absolute_uri,
                                      request_uri, method, body, headers,
                                      redirections, cachekey)

    def _conn_request(self, conn, request_uri, method, body, headers):
        try:
            return httplib2.Http._conn_request(self, conn, request_uri, method,
                                               body, headers)
        except BlockedError:
            conn.close()
            raise
