@ECHO off
set EC2_HOME=C:\EC2
set PATH=%PATH%;%EC2_HOME%\bin
set EC2_PRIVATE_KEY=C:\EC2\Pk.pem
set EC2_cert=c:\EC2\Cert.pem
set JAVA_HOME=C:\Program Files\Java\jre6
"%JAVA_HOME%\bin\java" -version