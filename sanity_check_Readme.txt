Sanity check

The approach is to create keywords and “compare” them with the ones kea has generated.

Perquisites: 
1.	Training has taken place and a model is generated.


Steps:

-	create a folder in KEAHOME directory  (e.g.  KEAHOME\my_testing)
-	select a subset of test documents from KEAHOME\testdocs and copy to  KEAHOME\my_testing
-	run KEAKeyphraseExtractor with parameter settings below: 
java kea.main.KEAKeyphraseExtractor -l KEAHOME\my_testing -m my_model  -v none -n 10

-	start the KEAServer: 
java patch.main.KEAServer path\to\my_model 8090

-	start python and import  the sanity_check.py, see listing below. 



sanity_check.py
‘’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’
import xmlrpclib
import os, glob

s = xmlrpclib.ServerProxy('http://127.0.0.1:8090')

#adjust your KEAHOME path
path = 'E:\\tmp\\kea-5.0_full\\my_testing\\'        
for infile in glob.glob( os.path.join(path, '*.txt') ):
    print "current file is: " + infile
    print "================================================================\n"     
    txt = open(infile).read()
    keywords = s.kea.extractKeyphrases(txt)    
    for str in keywords:
        print str     
        
    #print contents of corresponding .key file
    path, fi = os.path.split(infile) 
    name, ext = fi.rsplit('.')
    keaKeyFile = path+'\\'+name+'.key'
    print "\ncontents of corresponding .key file ", keaKeyFile ,"from KEA."
    print "........................................................................\n"
    txt = open(keaKeyFile).read()
    print txt
    
‘’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’

With two documents as input  

You get the following output from sanity_chek.py

current file is: E:\tmp\kea-5.0_full\my_testing\gtz_g24ine.txt
================================================================

'animal-powered mills'
'power gears'
Animal-Powered
'grinding unit'
grinding
gears
Mills
'motor mill'
FCFA
'draft animals'

contents of corresponding .key file  E:\tmp\kea-5.0_full\my_testing\gtz_g24ine.key from KEA.
........................................................................

animal-powered mills
power gears
Animal-Powered
grinding unit
grinding
gears
Mills
motor mill
FCFA
draft animals

current file is: E:\tmp\kea-5.0_full\my_testing\iirr_ii02re.txt
================================================================

upland
Agroforestry
Homegardens
hedgerows
'agroforestry systems'
biophysical
Trees
'Research and extension'
Forestry
'farm households'

contents of corresponding .key file  E:\tmp\kea-5.0_full\my_testing\iirr_ii02re.key from KEA.
........................................................................

upland
Agroforestry
Homegardens
hedgerows
agroforestry systems
biophysical
Trees
Research and extension
Forestry
farm households
