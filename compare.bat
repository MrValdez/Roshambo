@echo off
rem The purpose of this script is to compare between the c and py program. There has been a floating difference between the two.
call compile.bat > temp/py1.txt
echo done compiling

go.exe 1 0 > temp/c1.txt
echo variable 1 done

go.exe 100 > temp/py100.txt
echo python variable 100 done

go.exe 100 0 > temp/c100.txt

rem compare
diff temp/c1.txt temp/py1.txt | less
diff temp/c100.txt temp/py100.txt | less
