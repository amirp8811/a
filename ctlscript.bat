@echo off
rem START or STOP Services
rem ----------------------------------
rem Check if argument is STOP or START

if not ""%1"" == ""START"" goto stop

if exist C:\Users\Thomas\AnomiDateWeb\hypersonic\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\server\hsql-sample-database\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\ingres\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\ingres\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\mysql\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\mysql\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\postgresql\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\postgresql\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\apache\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\apache\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\openoffice\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\openoffice\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\apache-tomcat\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\apache-tomcat\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\resin\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\resin\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\jetty\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\jetty\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\subversion\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\subversion\scripts\ctl.bat START)
rem RUBY_APPLICATION_START
if exist C:\Users\Thomas\AnomiDateWeb\lucene\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\lucene\scripts\ctl.bat START)
if exist C:\Users\Thomas\AnomiDateWeb\third_application\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\third_application\scripts\ctl.bat START)
goto end

:stop
echo "Stopping services ..."
if exist C:\Users\Thomas\AnomiDateWeb\third_application\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\third_application\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\lucene\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\lucene\scripts\ctl.bat STOP)
rem RUBY_APPLICATION_STOP
if exist C:\Users\Thomas\AnomiDateWeb\subversion\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\subversion\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\jetty\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\jetty\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\hypersonic\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\server\hsql-sample-database\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\resin\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\resin\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\apache-tomcat\scripts\ctl.bat (start /MIN /B /WAIT C:\Users\Thomas\AnomiDateWeb\apache-tomcat\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\openoffice\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\openoffice\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\apache\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\apache\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\ingres\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\ingres\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\mysql\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\mysql\scripts\ctl.bat STOP)
if exist C:\Users\Thomas\AnomiDateWeb\postgresql\scripts\ctl.bat (start /MIN /B C:\Users\Thomas\AnomiDateWeb\postgresql\scripts\ctl.bat STOP)

:end

