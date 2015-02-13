@echo off
cls

gcc -w -m64 rsb-ts1-full.c python.c SFMT-src-1.4.1/SFMT.c -lm -I/Python34/include/ -ISFMT-src-1.4.1/ -Lpython_c_api/ -lpython -o full.exe
if %ERRORLEVEL% NEQ 1 full.exe