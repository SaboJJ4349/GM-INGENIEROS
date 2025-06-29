@echo off
echo ================================================
echo    CLICKUP EXPORTATOR GANTT - INICIALIZADOR
echo ================================================
echo.

echo [1/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instalar Python 3.9 o superior.
    pause
    exit
)

echo [2/4] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit
)

echo [3/4] Extrayendo datos desde ClickUp...
python main.py
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Error al extraer datos. Usando datos existentes o de ejemplo.
)

echo [4/4] Iniciando aplicacion Streamlit...
echo.
echo ================================================
echo  Aplicacion iniciandose en: http://localhost:8501
echo  Presiona Ctrl+C para detener la aplicacion
echo ================================================
echo.

streamlit run gantt_app.py

pause
