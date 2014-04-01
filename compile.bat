@echo off
cls
gcc -w -m64 rsb-ts1.c python.c -lm -I/Python34/include/ -Lpython_c_api/ -lpython
if %ERRORLEVEL% NEQ 1 a.exe