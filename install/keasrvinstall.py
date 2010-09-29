#! /usr/bin/env python
'''
Created on Sep 28, 2010

@author: Isaac
'''
import getpass
import os
#import urllib
import sys


class keasrvinstall(object):
    '''
    classdocs
    '''


    def __init__(self, java_port = 8000):
        '''
        set up some vars for doing the install
        modify to fit your installation
        the defaults should be fine however
        '''
        
        self.jv_port = java_port
        self.py_port = java_port +1
        self.start_jv = True
        self.start_py = True
        self.kea_user = 'keasrv'
        self.set_kea_pass = True
        self.kea_pass = 'RunKea4ME'
        self.kea_home = '/home/%s' % self.kea_user
        self.service_path = 'kea-service'
        self.kea_src_name = 'kea-5.0_full'
        self.kea_src_url = 'http://kea-algorithm.googlecode.com/files/'
        self.kea_default_model = 'kea-5.0-default_model'
        self.kea_default_model_url = 'http://metaoptimize.com/data/'
        self.kea_xmlrpc_jar = 'xmlrpc-1.2-b1.jar'
        self.kea_xmlrpc_jar_url = 'http://ftp.us.xemacs.org/pub/mirrors/maven2/xmlrpc/xmlrpc/1.2-b1'
        
        """ no modes below this point """
        self.wget_resorces = []
        self.wget_resorces.append({'path':'%s/%s.zip' % (self.kea_src_url, self.kea_src_name), 
                                   'get_check':'%s/%s.zip' % (self.kea_home, self.kea_src_name),
                                   'dest':'%s/%s' % (self.kea_home, self.kea_src_name),
                                   'unpack':'unzip',
                                   'unpack_check':'%s/%s'% (self.kea_home, self.kea_src_name), 
                                   'required':True})
        self.wget_resorces.append({'path' :'%s/%s' %(self.kea_xmlrpc_jar_url, self.kea_xmlrpc_jar),
                                   'check':self.kea_xmlrpc_jar,
                                   'dest':'%s/%s' % (self.kea_home,self.service_path),
                                   'required':True})
        self.wget_resorces.append({'path' : '%s/%s' % (self.kea_default_model_url, self.kea_default_model),
                                   'check': self.kea_default_model,
                                   'dest':'%s/%s/%s' % (self.kea_home, self.kea_src_name, self.kea_default_model),
                                   'required':False})
        
    def userCheck(self):
        print "user = ", getpass.getuser()
        if getpass.getuser() != 'root':
            print " the install script must be run as root"
            sys.exit()
        else:
            print " good were running as root"
    def createUser(self):
        """ create the user the service will run as """
        
        os.system('useradd %s -c "user for running kea as a service"' % (self.kea_user))
        print "created user %s" % self.kea_user
        if self.set_kea_pass:
            os.system("echo %s |passwd --stdin %s" % (self.kea_pass, self.kea_user))
            print "set password for %s" % self.kea_user
        else:
            print " not setting password for %s" % self.kea_user
              
              
if __name__ == "__main__":
    
    my_inst = keasrvinstall()              
    my_inst.userCheck()
    my_inst.createUser()
        