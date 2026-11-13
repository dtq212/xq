@echo off
rem Build astar_xq.c thanh astar_xq.dll (64-bit, khop Python 3.8 64-bit) bang MSVC (Visual Studio Build Tools).
rem   /O2  toi uu toc do        /LD  tao DLL        /fp:precise  so thuc giong Python (de ra dung y duong)
rem   /MT  nhung san thu vien C vao DLL => may khac khong can cai Visual C++ Redistributable
setlocal
cd /d "%~dp0"
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (
    echo Khong thay vswhere.exe: chua cai Visual Studio Build Tools
    exit /b 1
)
rem Ghi ra file tam roi doc lai: dau ngoac trong "Program Files (x86)" lam for /f cua cmd hieu sai
set "VSDIR="
"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath > "%TEMP%\xq_vsdir.txt"
set /p VSDIR=<"%TEMP%\xq_vsdir.txt"
del /q "%TEMP%\xq_vsdir.txt" 2>nul
if not defined VSDIR (
    echo Build Tools chua co bo C++ x64 ^(Desktop development with C++^)
    exit /b 1
)
rem vcvarsall tu goi vswhere.exe qua PATH va bao loi vo hai "'vswhere.exe' is not recognized": an di (cl hong thi van bao loi o duoi)
call "%VSDIR%\VC\Auxiliary\Build\vcvarsall.bat" x64 >nul 2>nul || exit /b 1
cl /nologo /O2 /LD /MT /fp:precise /W3 astar_xq.c /Fe:astar_xq.dll /link /NOLOGO || exit /b 1
del /q astar_xq.obj astar_xq.lib astar_xq.exp 2>nul
echo Da build astar_xq.dll
