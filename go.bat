@echo off
gcc -m64 rsb-ts1.c yomi.c -lm
if %ERRORLEVEL% NEQ 1 a.exe