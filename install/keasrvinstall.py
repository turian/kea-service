#! /usr/bin/env python
'''
Created on Sep 28, 2010

@author: Isaac Jessop
'''
import getpass
import commands
import os
import urllib
import sys


class keasrvinstall(object):
    '''
    A class for installing the kea service on an AWS EC2 instance
    '''


    def __init__(self, java_port = 8000, install_path = '/var/opt' , user_name = 'keasrv'):
        '''
        optionally pass a port, install path and user to the init method
        set up some vars for doing the install
        modify to fit your installation
        the defaults should be fine however
        '''
        ########## begin install params definition ###############
        # the port the java server will listen on default = 8000
        self.jv_port = java_port
        # the port the python wrapper will listen on
        self.py_port = java_port +1
        # where the service will be installed
        self.kea_base_path = install_path
        # where the pid of the running java process will be stored by the init script
        # when the process starts. used by the init script to kill the process
        self.jv_pid_file = '/var/run/keasrv_jv.pid'
        # where the pid of the running python wrapper process will be stored by the init script
        # when the process starts. used by the init script to kill the process
        self.py_pid_file = '/var/run/keasrv_py.pid'
        # the location of the python wrapers log file
        self.kea_py_log = '/var/log/kea-service_py.log'
        # the location of the java servers log file
        self.kea_jv_log = '/var/log/kea-service_jv.log'
        # the user name the server will run as
        self.kea_user = user_name
        # flag to control weather or not a password is set for the user
        self.set_kea_pass = False
        # the users password if set
        self.kea_pass = 'RunKea4ME'
        
        ###################### end install params definition ###############
        ##
        ## don't change definitions below this point
        ##
        ####################################################################
        
        self.conf_path = "/etc/kea-service.conf" 
        self.kea_src_name = 'kea-5.0_full'
        self.kea_home = '%s/%s' % (self.kea_base_path, self.kea_user)
        self.service_path = 'kea-service'
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
        self.kea_resorces.append({'yum_install':'yum -y install python24',
                                  'whereis_query':'python24',
                                  'whereis_fail':'python24:',
                                  'res_name':'python 2.4'})
        
    def userCheck(self):
        """ make sure we are the root user """
        # make sure we are running as root
        # if not warn and exit
        print "user = ", getpass.getuser()
        if getpass.getuser() != 'root':
            print " the install script must be run as root"
            self.usage()
            sys.exit()
        else:
            print " good were running as root"
            
    def createUser(self):
        """ create the user the service will run as """
        
        # create the user and set the password if requested
        os.system('useradd %s -d %s/%s -c "user for running kea as a service"' % (self.kea_user, self.kea_base_path, self.kea_user))
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
            if res.has_key('dest') and os.path.exists(res['dest']): 
                print "%s exists skipping if you want to update it delete the existing file" % res['dest']
                continue
            # make the dest dir if needed
            if res.has_key('mkdir'):
                os.makedirs(res['mkdir'])
             
            # if its a git resource use git to retrive it else use urllib    
            if res.has_key('git_cmd'):
                curent_dir = os.getcwd()
                os.chdir(res['dest'])
                os.system("%s %s" % (res['git_cmd'], res['path']))
                os.chdir(curent_dir)
            # if it has a yum install key its a resource needing instal by yum
            elif res.has_key('yum_install'):
                # check to see if the resource is already installed
                if commands.getoutput('whereis %s' % res['whereis_query']) == res['whereis_fail']:
                    print "\n\nInstalling %s" % res['res_name']
                    # execute the yum install
                    py_inst_result = commands.getoutput(res['yum_install'])
                    print py_inst_result
                    # check for yum's last line complete message
                    if py_inst_result.split('\n')[-1].find('Complete') > -1:
                        print " %s install completed" % res['res_name']
                    else:
                        # looks like the yum install failed so print a message
                        # and exit
                        print "fatal error could not install %s" % res['res_name']
                        sys.exit()
                else:
                    print "%s already installed" % res['res_name']
            else: 
                # default to using urllib to get the resource
                print "fetching %s writing to %s" % (res['path'], res['dest'])
                urllib.urlretrieve(res['path'], res['dest'], self.dlStatus, data=None)
                
            
            #unpack if needed
            if res.has_key('unpack'):
                os.system("/usr/bin/unzip %s -d %s" % (res['dest'],res['unpack_dest']))
        
        print "\n\n resource download and install complete"
        
    def copySrvc(self):
        """ copy the src files to the install dir """
        # copy the files from the package to the install location
        # set group owner and permissions on the files 
        os.system('cp -r ../../kea-service/* %s/kea-service/. ' % self.kea_home)
        os.system("chgrp -R %s %s/*" % (self.kea_user, self.kea_home))
        os.system("chown -R %s %s/*" % (self.kea_user, self.kea_home))
        os.system("chmod +x %s/kea-service/python-server-wrapper.py" % (self.kea_home))
        
        
    def makeConf(self):
        """ create the init.d script """
        # open the config file
        # and write out all the config parameters
        fout = open(self.conf_path,'w')
        fout.write("## kea-service init configuration -- created by the kea-service installer") 
        fout.write("#\n#\n")
        fout.write("KEAHOME=%s\n" % self.kea_home )
        fout.write("KEAJARS=%s\n" % self.kea_src_name)
        fout.write("KEAMODEL=%s\n" % self.kea_default_model)
        fout.write("JAVASRV=%s\n" % self.kea_java_exe)
        fout.write("JVPORT=%s\n" % self.jv_port)
        fout.write("PYPORT=%s\n" % self.py_port)
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
        # get the current run level
        run_level = commands.getoutput('/sbin/runlevel').split()[1]
        # create the start and stop links in the current run level
        os.system("ln -s /etc/init.d/keasrvctl /etc/rc.d/rc%s.d/S99Keasrv" % run_level)
        os.system("ln -s /etc/init.d/keasrvctl /etc/rc.d/rc%s.d/K99Keasrv" % run_level)
        for fpath in [self.kea_jv_log, self.kea_py_log ]:
            fout = open(fpath,'w')
            fout.write(" kiea service installed \n")
            fout.close()
            os.system("chmod 664 %s" % fpath)
            os.system("chgrp %s %s" % (self.kea_user, fpath))
    
    def usage(self, reason = 'user'):
            if reason == 'port':
                print "%s is not a valid port" % sys.argv[1]
            print "usage: sudo %s portnumber \n or" % sys.argv[0]
            print "usage: sudo %s portnumber install_path \n or" % sys.argv[0]
            print "usage: sudo %s portnumber install_path user" % sys.argv[0]
        
if __name__ == "__main__":
    
    # if we have a port specified on the command line
    if len(sys.argv) > 1:
        # make sure the port is a number
        try:
            jv_port = int(sys.argv[1])
        except ValueError:
            keasrvinstall().usage("port")
            sys.exit(1)
    else:
        jv_port = 8000
        
    # if we have a install location specified on the command line
    if len(sys.argv) > 2:
        install_path = sys.argv[2]
    else:
        #default install path
        install_path = "/var/opt"
        
    # if we have a user specified on the command line
    if len(sys.argv) > 3:
        install_user = sys.argv[3]
    else:
        # default user name
        install_user = "keasrv"
        
    # create an instance of the  keasrvinstall class
    # pass it the port install path and user name   
    my_inst = keasrvinstall(jv_port, install_path, install_user)              
    # make sure we are running as root
    my_inst.userCheck()
    # create the user and install location
    my_inst.createUser()
    # get all the resources we need to make it run
    my_inst.getResources()
    # move the files from the packeg that we need
    # to the install path
    my_inst.copySrvc()
    # create the configuration file
    my_inst.makeConf()
    # install the init scripts
    my_inst.instInitScript()
    
    print "Installation complete "
    print "kea service installed at %s/%s listening on port %s and %s" % (my_inst.kea_base_path,
                                                                          my_inst.kea_user, 
                                                                          my_inst.jv_port,
                                                                          my_inst.py_port)
    print "config file"
    print my_inst.conf_path
    print "log files"
    print my_inst.kea_jv_log
    print my_inst.kea_py_log

    print "to start the service"
    print "sudo /etc/init.d/keasrvctl start"