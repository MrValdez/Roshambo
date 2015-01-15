@echo off
cls

gcc -w -m64 rsb-ts1-full.c python.c -lm -I/Python34/include/ -Lpython_c_api/ -lpython -o full.exe
if %ERRORLEVEL% NEQ 1 full.exe