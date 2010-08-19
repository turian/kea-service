Sanity check

The approach is to create keywords and compare them with the ones kea has generated.

This is for Windows. If you are under Unix, you should use ./sanity_check_files.py

Prequisites: 
1.	Training has taken place and a model is generated. e.g.
    java kea.main.KEAModelBuilder -d -l testdocs/en/train/ -m my_model -v none -f skos

You can extract keyphrases for some test documents given this model:
    java kea.main.KEAKeyphraseExtractor -l testdocs/en/test -m my_model -v none -f text


Steps:

-	create a folder in KEAHOME directory (e.g.  KEAHOME\my_testing)
-	select and copy a subset of test documents from KEAHOME\testdocs to KEAHOME\my_testing
- copy sanity_check.py into KEAHOME
- perform the check by typing command below:
			
			python sanity_check.py <port> <folder> <model>
		
		e.g.
		
			python sanity_check.py 8090 my_testing mymodel

With two documents as input you get the following output from sanity_chek.py

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
