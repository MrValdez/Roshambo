@echo off
gcc -m64 yomi.c rsb-ts1.c -lm
if %ERRORLEVEL% NEQ 1 a.exe