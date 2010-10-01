#!/bin/env python
"""
Python XML-RPC server wrapper for KEA.
If the Java KEA service throws an exception, return an empty list of
keywords. This appears to happen on weird Unicode characters, in 0.3%
of page text. YMMV.
"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import xmlrpclib
s = xmlrpclib.ServerProxy('http://localhost:8000')

import sys

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("0.0.0.0", 8001),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

from common.movingaverage import MovingAverage
broke = MovingAverage()
def extractKeyphrases(txt):
    if broke.cnt % 100 == 0:
        print >> sys.stderr, "%s documents could NOT have keyphrase extracted" % broke
    try:
        kw = s.kea.extractKeyphrases(txt)
        broke.add(0)
        return kw
    except:
        print >> sys.stderr, "Oops! Couldn't extract keyphrases over:", repr(txt)
        broke.add(1)
        return []

server.register_function(extractKeyphrases)

# Run the server's main loop
server.serve_forever()

