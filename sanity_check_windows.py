#!/usr/bin/env python

from shutil import copy
from shutil import rmtree

import xmlrpclib
import glob, os, sys, time

'''
This python module is meant to perform a sanity check for XML-RPC Service in KEA 5.0. 
The check is performed according to following steps:
- Given a set of .txt files have the stand alone KEA output .key files into provided folder, 
- Start the XML-RPC service on localhost using provided port,
- Have it generate corresponding set of key phrases and 
- Print out both sets into console for compare

'''

#Read the port number 
PORT=sys.argv[1]
print "PORT= %s"%PORT

KEA_HOME=os.environ.get("KEAHOME")
if KEA_HOME == None:
	os.system("setenv.bat")

#Read test folder
TEST_DIR=KEA_HOME+"\\"+sys.argv[2]
print "TEST_DIR= ", TEST_DIR
	 
#Read the model 
MY_MODEL = sys.argv[3]
PATCH_LIB=KEA_HOME+"\\patch\\kea_server.jar"

#adjust the xmlrpc library path
XMLRPC_LIB="E:\\programs\\tools\\xmlrpc-1.2-b1\\xmlrpc-1.2-b1.jar"


print "Delete existing .key files in %s prior KEA keyword extraction" %TEST_DIR
if os.path.exists(TEST_DIR):
	for keyFile in glob.glob( os.path.join(TEST_DIR, '*.key') ):
		os.remove(keyFile)

print "Running KEA keyword extraction..."
JAVA=os.environ.get("JAVA_HOME")+"\\bin\\java.exe"
os.system("%s kea.main.KEAKeyphraseExtractor -l %s -m %s -v none -n 10 "%(JAVA, TEST_DIR, MY_MODEL))

print "Done keyword extraction, find generated .key files in %s" %TEST_DIR

print "Starting server on port %s" %PORT
TEST_CLASSPATH="%s;%s;%s"%(PATCH_LIB, XMLRPC_LIB, os.environ.get("CLASSPATH"))
KEA_SERVER_START="%s -cp %s patch.main.KEAServer %s %s"%(JAVA, TEST_CLASSPATH, MY_MODEL, PORT)
#print "Server start command %s" %KEA_SERVER_START

print 
#os.system(("start \'Running KEA XMLRPC Service\' cmd /C %s %s ")%(KEA_SERVER_START, PORT))

#Start KEA XMLRPC Service
os.system("start \"%s\" cmd /C %s "%('Running KEA XMLRPC Service', KEA_SERVER_START))

print "\nWaiting 10 seconds for KEA XMLRPC Service to come up..."  
a = 0
while a < 10:
	time.sleep(1)
	a= a+1
	print "."

print "Done waiting"

#Start the WebServer 

KEA_SERVER = xmlrpclib.ServerProxy('http://127.0.0.1:'+PORT)

for infile in glob.glob( os.path.join(TEST_DIR, '*.txt') ):
    print "current file is: " + infile
    print "================================================================\n"

    txt = open(infile).read()
    keywords = KEA_SERVER.kea.extractKeyphrases(txt)
    for str in keywords:
        print str
        
    #print contents of corresponding .key file
    path, fi = os.path.split(infile)
    name, ext = fi.rsplit('.')
    keaKeyFile = path+'\\'+name+'.key'
    print "\ncontents of corresponding .key file ", keaKeyFile ," from KEA."
    print "........................................................................\n"
    txt = open(keaKeyFile).read()
    print txt
    
print "All Done."
