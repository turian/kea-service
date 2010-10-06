#!/bin/env python2.4
"""
Python XML-RPC server wrapper for KEA.
If the Java KEA service throws an exception, return an empty list of
keywords. This appears to happen on weird Unicode characters, in 0.3%
of page text. YMMV.
"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import xmlrpclib
import sys
# if we are passed a port use it
# else use 8000 
if len(sys.argv) > 1:
    jv_port = int(sys.argv[0])
else:
    jv_port = 8000

print "jv_port = ", jv_port

s = xmlrpclib.ServerProxy('http://localhost:%d' % jv_port)

import sys

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("0.0.0.0", jv_port + 1),
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

