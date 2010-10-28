import paranoidlib

# Overwrite the DNS library's gethostbyname to None by default so we get an
# exception if a non-stubbed call is executed.
paranoidlib.gethostbyname = None


def test_init():
    h = paranoidlib.Http()
    assert h

