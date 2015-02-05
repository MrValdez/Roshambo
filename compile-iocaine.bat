@echo off
cls

gcc -w -m64 rsb-iocaine.c python.c -lm -I/Python34/include/ -Lpython_c_api/ -lpython -o iocaine.exe
if %ERRORLEVEL% NEQ 1 iocaine.exe