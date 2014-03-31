rem set file=c:\Python34\DLLs\python3.dll
set file=..\python3.dll

pexports %file% > python.def
dlltool --dllname %file% --def python.def --output-lib libpython.a