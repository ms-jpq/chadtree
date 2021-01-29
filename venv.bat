
cd /D "%~dp0"
set "path=%cd%\.vars\runtime\Scripts;%PATH%"
set "py3_exe=%cd%\.vars\runtime\Scripts\python.exe"

if exist "%1" (
  if exist "%py3_exe%" (
    shift
    "%py3_exe%" %*
  ) else (
    %*
  )
) else (
  %*
)

exit -b %ERRORLEVEL%
@echo on
