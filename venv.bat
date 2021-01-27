@echo off
cd /D "%~dp0"
set path=%cd%\.vars\runtime\Scripts;%PATH%
IF EXIST %1 (
  SHIFT
  python %*
) ELSE (
  %*
)
@echo on
