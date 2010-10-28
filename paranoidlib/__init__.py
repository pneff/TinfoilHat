"""
httplib2 extension that is more paranoid about input. Won't allow downloading
data from private or internal IPs.

Inspired by, but not yes as paranoid as, LWPx::ParanoidAgent.
"""
__version__ = "0.1"
__author__ = [
    "Patrice Neff <software@patrice.ch>",
]


import httplib2

class Http(httplib2.Http):
    pass

