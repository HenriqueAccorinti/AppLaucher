@echo off
echo ============================================
echo   Project Launcher - Build para .exe
echo ============================================
echo.

echo [1/3] Instalando dependencias...
pip install pywebview pyinstaller --quiet
if errorlevel 1 (
    echo ERRO ao instalar dependencias.
    pause & exit /b 1
)

echo [2/3] Gerando executavel (pode demorar 1-2 min)...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "Project Launcher" ^
  project_launcher_app.py

if errorlevel 1 (
    echo ERRO ao gerar executavel.
    pause & exit /b 1
)

echo [3/3] Limpando arquivos temporarios...
rmdir /s /q build 2>nul
del "Project Launcher.spec" 2>nul

echo.
echo ============================================
echo   Pronto!  dist\Project Launcher.exe
echo ============================================
echo.
echo Os dados ficam em projects_data.json
echo na mesma pasta do .exe.
echo.
pause