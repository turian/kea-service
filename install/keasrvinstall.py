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
        self.start_jv = True
        self.start_py = True
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
        self.kea_python_common_url = 'http://github.com/turian'
        self.kea_python_common_name = 'common'
        self.kea_py_common_path = 'py_common'
        
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
        self.kea_resorces.append({'path' : '%s/%s' % (self.kea_python_common_url, self.kea_python_common_name),
                                   'dest':'%s/%s/%s' % (self.kea_home, self.kea_py_common_path, self.kea_python_common_name),
                                   'mkdir':'%s/%s' % (self.kea_home, self.kea_py_common_path),
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
                
            rt = urllib.urlretrieve(res['path'], res['dest'], self.dlStatus, data=None)
            dir(rt)
            
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
        
        
    def makeScript(self):
        """ create the init.d script """
        
        script_path = "%s/keasrvctl" % self.kea_home
        fout = open(script_path,'w')
        fout.write("#!/bin/bash \n\n")
        fout.write("#control script for starting and stopping the kea service \n\n")
        
        fout.write("prog=keasrvctl\n")
        if self.start_jv:
            fout.write("JAVA_RUN=/var/run/keasrv_j.pid \n")
            
        if self.start_py:
            fout.write("PY_RUN=/var/run/keasrv_p.pid\n")
            
        fout.write("# Source function library.\n")
        fout.write(". /etc/rc.d/init.d/functions \n")
        
        clp_export_string = """export CLASSPATH="%s/kea-service/kea_server.jar:""" % self.kea_home
        clp_export_string = "%s%s/kea-5.0_full:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/commons-logging.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/icu4j_3_4.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/iri.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/jena.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/snowball.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/weka.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/xercesImpl.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = "%s%s/kea-5.0_full/lib/kea-5.0.jar:" % (clp_export_string, self.kea_home)
        clp_export_string = """%s%s/kea-service/xmlrpc-1.2-b1.jar" \n\n""" % (clp_export_string, self.kea_home)
        
        fout.write(clp_export_string)
        
        py_export_string = """export PYTHONPATH=".:%s/py_common" \n\n""" % self.kea_home
        fout.write(py_export_string)
        start_code = """\n
        \nstart() {
        \n    echo -n $"Starting $prog: "
        \n    JV_RETVAL=0
        \n    PY_RETVAL=0
        """
        fout.write(start_code)
        if self.start_jv:
            start_code ="""
                \n    if [ -f $JAVA_RUN ]; then
                \n       PID=`cat $JAVA_RUN`
                \n       echo java version of kea-service is already running: $PID
                \n       exit 2;
                \n    fi """
                
            fout.write(start_code)
        if self.start_py:
            start_code ="""
                \n    if [ -f $PY_RUN ]; then
                \n       PID=`cat $PY_RUN`
                \n       echo python version of kea-service is already running: $PID
                \n       exit 2;
                \n    fi """
                
            fout.write(start_code)
        if self.start_jv:
            start_code ="""
            \n    echo -n $"starting kea-service java damon $prog "
            \n    cd %s/%s
            \n    nohup java patch.main.KEAServer %s %s &""" % (self.kea_home, self.kea_src_name, self.kea_default_model ,self.jv_port)
            fout.write(start_code)
            start_code = """
                \n    JV_RETVAL=$?
                \n    echo
                \n    [ $JV_RETVAL -eq 0 ] && grep patch.main.KEAServer /proc/*/cmdline | cut -d/ -f3 | head -1 > $JAVA_RUN 
                """ 
            fout.write(start_code)
        if self.start_py:
            start_code ="""
            \n    echo -n $"starting kea-service python damon $prog "
            \n     %s/kea-service/python-server-wrapper.py &""" % (self.kea_home)
            fout.write(start_code)
            start_code = """
                \n    PY_RETVAL=$?
                \n    echo
                \n    [ $PY_RETVAL -eq 0 ] && grep python-server-wrapper.py /proc/*/cmdline | cut -d/ -f3 | head -1  > $PY_RUN 
                """ 
                
            fout.write(start_code)
        start_code ="""
            \n    RETVAL=$?
            \n    echo
            \n    [ $PY_RETVAL -eq 0 ] && [ $JV_RETVAL -eq 0 ]
            \n}"""
        
        fout.write(start_code)
        stop_code = """\n
            \nstop() {
            \n    echo -n $"Stopping $prog:" """
        fout.write(stop_code)
        if self.start_py:
            stop_code = """
                \n    killproc -p $PY_RUN 
                \n    PY_RETVAL=$?
                \n    echo
                \n    [ $PY_RETVAL = 0 ] && rm -f $PY_RUN"""
            fout.write(stop_code)
        if self.start_jv:
            stop_code = """
                \n    killproc -p $JAVA_RUN 
                \n    JV_RETVAL=$?
                \n    echo
                \n    [ $JV_RETVAL = 0 ] && rm -f $JAVA_RUN"""
            fout.write(stop_code)
            
        stop_code ="""
            \n    RETVAL=$?
            \n    echo
            \n    [ $PY_RETVAL -eq 0 ] && [ $JV_RETVAL -eq 0 ]
            \n}"""
        
        fout.write(stop_code)
        
        case_block = """\n# See how we were called.\ncase "$1" in 
          \n    start)
          \n        start
          \n        ;;
          \n    stop)
          \n        stop
          \n        ;;
          \n    status)
          \n        status 
          \n        RETVAL=$?
          \n        ;;
          \n    restart)
          \n        stop
          \n        start
          \n        ;;
          \n    *)
          \n        echo $"Usage: $prog {start|stop|restart|status}"
          \n        RETVAL=3
        \nesac"""
        fout.write(case_block)
        fout.close()
    
if __name__ == "__main__":
    
    my_inst = keasrvinstall()              
    my_inst.userCheck()
    my_inst.createUser()
    my_inst.getResources()
    my_inst.copySrvc()
    my_inst.makeScript()
