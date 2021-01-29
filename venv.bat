@echo off
cd /D "%~dp0"
set "path=%cd%\.vars\runtime\Scripts;%PATH%"

i exist "%1" (
  if exist "%cd%\.vars\runtime\Scripts\python.exe" (
    shift
    python %*
  ) else (
    %*
  )
) else (
  %*
)
@echo on
