@ECHO OFF
set MSYSTEM=msys
if not exist c:\msys64\usr\bin\bash.exe (
    echo.
    echo You must install msy2-x86_64 at C:\msys64
    echo if you didn't install, please install
    echo http://repo.msys2.org/distrib/x86_64/msys2-x86_64-20161025.exe
	echo.
	ping -n 10 127.0.0.1>nul
    exit 1	
	)
c:\msys64\usr\bin\bash.exe  --init-file ./init.sh -i
