@echo off
cls

rem note: yomi.c is only added to make it easy to transition between c code and python code

gcc -w -m64 rsb-ts1.c python.c yomi.c -lm -I/Python34/include/ -Lpython_c_api/ -lpython -o go.exe
if %ERRORLEVEL% NEQ 1 go.exe