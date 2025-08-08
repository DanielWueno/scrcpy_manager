REM filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\install_ios_tools_windows.bat
@echo off
echo Instalando herramientas iOS para Windows...

REM Crear directorio de herramientas
mkdir C:\tools 2>nul
mkdir C:\tools\libimobiledevice 2>nul
mkdir C:\tools\ios_video_stream 2>nul

echo.
echo === Instalando libimobiledevice ===
echo.
echo Opcion 1: Usar Chocolatey (recomendado)
echo   choco install libimobiledevice
echo.
echo Opcion 2: Descarga manual
echo   1. Ve a: https://github.com/libimobiledevice-win32/imobiledevice-net/releases
echo   2. Descarga libimobiledevice-win64.zip
echo   3. Extrae a C:\tools\libimobiledevice\
echo.

echo === Instalando ios_video_stream ===
echo.
echo 1. Ve a: https://github.com/nanoscopic/ios_video_stream/releases
echo 2. Descarga ios_video_stream-windows.zip
echo 3. Extrae a C:\tools\ios_video_stream\
echo.

echo === Verificando instalacion ===
echo.
if exist "C:\tools\libimobiledevice\idevice_id.exe" (
    echo [OK] libimobiledevice encontrado
    C:\tools\libimobiledevice\idevice_id.exe --version
) else (
    echo [FALTA] libimobiledevice no encontrado
)

if exist "C:\tools\ios_video_stream\ios_video_stream.exe" (
    echo [OK] ios_video_stream encontrado
) else (
    echo [FALTA] ios_video_stream no encontrado
)

echo.
echo Instalacion completada. 
echo Conecta un dispositivo iOS via USB y reinicia la aplicacion.
pause