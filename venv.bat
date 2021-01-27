@echo off
cd /D "%~dp0"
set path=%cd%\.vars\runtime\bin;%PATH%
@echo on


echo %path%
echo $*
