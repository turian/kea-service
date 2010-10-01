#! /usr/bin/env python
'''
Created on Sep 28, 2010

@author: Isaac
'''
import getpass
import os
import urllib
import sys


class keasrvinstall(object):
    '''
    classdocs
    '''


    def __init__(self, java_port = 8001):
        '''
        set up some vars for doing the install
        modify to fit your installation
        the defaults should be fine however
        '''
        
        self.jv_port = java_port
        self.py_port = java_port +1
        self.jv_pid_file = '/var/run/keasrv_jv.pid'
        self.py_pid_file = '/var/run/keasrv_py.pid'
        self.kea_py_log = '/var/log/kea-service_py.log'
        self.kea_jv_log = '/var/log/kea-service_jv.log'
        self.kea_user = 'keasrv'
        self.set_kea_pass = True
        self.kea_pass = 'RunKea4ME'
        self.kea_home = '/home/%s' % self.kea_user
        self.service_path = 'kea-service'
        self.kea_src_name = 'kea-5.0_full'
        self.kea_src_url = 'http://kea-algorithm.googlecode.com/files'
        self.kea_default_model = 'kea-5.0-default_model'
        self.kea_default_model_url = 'http://metaoptimize.com/data'
        self.kea_xmlrpc_jar = 'xmlrpc-1.2-b1.jar'
        self.kea_xmlrpc_jar_url = 'http://ftp.us.xemacs.org/pub/mirrors/maven2/xmlrpc/xmlrpc/1.2-b1'
        self.kea_python_common_url = 'git://github.com/turian/common.git'
        self.kea_python_common_name = 'common'
        self.kea_py_common_path = 'py_common'
        self.kea_java_exe = 'patch.main.KEAServer'
        self.kea_python_exe = 'python-server-wrapper.py'
        
        """ no modes below this point """
        self.kea_resorces = []
        # define kea source resource parameters
        self.kea_resorces.append({'path':'%s/%s.zip' % (self.kea_src_url, self.kea_src_name), 
                                   'get_check':'%s/%s.zip' % (self.kea_home, self.kea_src_name),
                                   'dest':'%s/%s.zip' % (self.kea_home, self.kea_src_name),
                                   'unpack':'unzip',
                                   'unpack_dest': self.kea_home,
                                   'unpack_check':'%s/%s'% (self.kea_home, self.kea_src_name), 
                                   'required':True})
        # define xmlrpc resource parameters
        self.kea_resorces.append({'path' :'%s/%s' %(self.kea_xmlrpc_jar_url, self.kea_xmlrpc_jar),
                                   'dest':'%s/%s/%s' % (self.kea_home, self.service_path, self.kea_xmlrpc_jar),
                                   'mkdir':'%s/%s' % (self.kea_home, self.service_path),
                                   'required':True})
        # define default model resource parameters
        self.kea_resorces.append({'path' : '%s/%s' % (self.kea_default_model_url, self.kea_default_model),
                                   'dest':'%s/%s/%s' % (self.kea_home, self.kea_src_name, self.kea_default_model),
                                   'required':False})
        # define python common resource parameters
        self.kea_resorces.append({'path' : '%s' % (self.kea_python_common_url),
                                   'dest':'%s/%s' % (self.kea_home, self.kea_py_common_path),
                                   'mkdir':'%s/%s' % (self.kea_home, self.kea_py_common_path),
                                   'git_cmd':'git clone ',
                                   'required':True})
        
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
            
    def dlStatus(self, blocks_read, block_size, total_size):
        """ a method to provide status of down load progress """
        if not blocks_read:
            print 'Connection opened'
            return
        if total_size < 0:
            # Unknown size
            print 'Read %d blocks' % blocks_read

        else:
            amount_read = blocks_read * block_size
            out_string = 'Read %d blocks, or %d/%d' % (blocks_read, amount_read, total_size)
            ps_string = "\b" * len(out_string)
            sys.stdout.write("%s%s" % (out_string, ps_string))
            return
            
    def getResources(self):
        """ loop through the resources down load and install them """
        for res in self.kea_resorces:
            # if the file already exists at the destination go to the next file
            if os.path.exists(res['dest']): 
                print "%s exists skipping if you want to update it delete the existing file" % res['dest']
                continue
            print "fetching %s writing to %s" % (res['path'], res['dest'])
            # make the dest dir if needed
            if res.has_key('mkdir'):
                os.makedirs(res['mkdir'])
             
            # if its a git resource use git to retrive it else use urllib    
            if res.has_key('git_cmd'):
                curent_dir = os.getcwd()
                os.chdir(res['dest'])
                os.system("%s %s" % (res['git_cmd'], res['path']))
                os.chdir(curent_dir)
            else: 
                
                urllib.urlretrieve(res['path'], res['dest'], self.dlStatus, data=None)
                
            
            #unpack if needed
            if res.has_key('unpack'):
                os.system("/usr/bin/unzip %s -d %s" % (res['dest'],res['unpack_dest']))
        
        print "\n\n resource download and install complete"
        
    def copySrvc(self):
        """ copy the src files to the install dir """
        
        os.system('cp -r ../../kea-service/* %s/kea-service/. ' % self.kea_home)
        os.system("chgrp -R %s %s/*" % (self.kea_user, self.kea_home))
        os.system("chown -R %s %s/*" % (self.kea_user, self.kea_home))
        os.system("chmod +x %s/kea-service/python-server-wrapper.py" % (self.kea_home))
        
        
    def makeConf(self):
        """ create the init.d script """
        
        conf_path = "/etc/kea-service.conf" 
        fout = open(conf_path,'w')
        fout.write("## kea-service init configuration -- created by the kea-service installer") 
        fout.write("#\n#\n")
        fout.write("KEAHOME=%s\n" % self.kea_home )
        fout.write("KEAJARS=%s\n" % self.kea_src_name)
        fout.write("KEAMODEL=%s\n" % self.kea_default_model)
        fout.write("JAVASRV=%s\n" % self.kea_java_exe)
        fout.write("JVPORT=%s\n" % self.jv_port)
        fout.write("JAVALOG=%s\n" % self.kea_jv_log)
        fout.write("PYSERV=%s\n" % self.kea_python_exe)
        fout.write("PYLOG=%s\n" % self.kea_py_log)
        fout.write("JAVA_RUN=%s\n" % self.jv_pid_file)
        fout.write("PY_RUN=%s\n" % self.py_pid_file)
        fout.write("SRVUSER=%s\n" % self.kea_user)
        fout.close()
        
    def instInitScript(self):
        """ copy the init script to the init.d dir and chmod it to make it ececutable """
        print "Installing init scripts"
        os.system("cp keasrvctl /etc/init.d/keasrvctl")
        os.system("chmod 755 /etc/init.d/keasrvctl")
        for fpath in [self.kea_jv_log, self.kea_py_log ]:
            fout = open(fpath,'w')
            fout.write(" kiea service installed \n")
            fout.close()
            os.system("chmod 666 %s" % fpath)
        
if __name__ == "__main__":
    
    my_inst = keasrvinstall()              
    my_inst.userCheck()
    my_inst.createUser()
    my_inst.getResources()
    my_inst.copySrvc()
    my_inst.makeConf()
    my_inst.instInitScript()
