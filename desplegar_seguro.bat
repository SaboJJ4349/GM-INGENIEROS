@echo off
echo 🔐 SCRIPT DE VERIFICACION Y DESPLIEGUE SEGURO
echo ============================================

echo.
echo 🔍 Ejecutando verificaciones de seguridad...
python verificar_seguridad.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ VERIFICACIONES FALLARON
    echo No se puede continuar con el despliegue
    pause
    exit /b 1
)

echo.
echo ✅ Verificaciones pasaron correctamente
echo.

echo 🚀 Opciones de despliegue:
echo 1. Ejecutar localmente
echo 2. Preparar para Streamlit Cloud
echo 3. Generar Docker
echo 4. Salir
echo.

set /p opcion="Selecciona una opcion (1-4): "

if "%opcion%"=="1" goto local
if "%opcion%"=="2" goto streamlit_cloud
if "%opcion%"=="3" goto docker
if "%opcion%"=="4" goto fin

echo Opcion no valida
goto fin

:local
echo.
echo 🖥️ EJECUTANDO LOCALMENTE...
echo Asegurate de tener configurado:
echo - CLICKUP_API_TOKEN
echo - CLICKUP_SPACE_ID
echo O tener el archivo .streamlit/secrets.toml
echo.
streamlit run gantt_app.py
goto fin

:streamlit_cloud
echo.
echo ☁️ PREPARANDO PARA STREAMLIT CLOUD...
echo.
echo 📋 CHECKLIST:
echo [ ] Codigo subido a GitHub
echo [ ] Secrets configurados en Streamlit Cloud
echo [ ] .gitignore incluido
echo.
echo 🔗 Pasos siguientes:
echo 1. Ve a https://share.streamlit.io
echo 2. Conecta tu repositorio GitHub
echo 3. Configura secrets en Settings ^> Secrets
echo 4. Deploy!
echo.
echo Presiona cualquier tecla cuando hayas completado estos pasos...
pause
goto fin

:docker
echo.
echo 🐳 GENERANDO CONFIGURACION DOCKER...
echo.

echo FROM python:3.9-slim > Dockerfile
echo. >> Dockerfile
echo WORKDIR /app >> Dockerfile
echo. >> Dockerfile
echo COPY requirements.txt . >> Dockerfile
echo RUN pip install -r requirements.txt >> Dockerfile
echo. >> Dockerfile
echo COPY . . >> Dockerfile
echo. >> Dockerfile
echo EXPOSE 8501 >> Dockerfile
echo. >> Dockerfile
echo HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health >> Dockerfile
echo. >> Dockerfile
echo ENTRYPOINT ["streamlit", "run", "gantt_app.py", "--server.port=8501", "--server.address=0.0.0.0"] >> Dockerfile

echo web: streamlit run gantt_app.py --server.port=$PORT --server.address=0.0.0.0 > Procfile

echo.
echo ✅ Archivos Docker generados:
echo - Dockerfile
echo - Procfile
echo.
echo 🐳 Para construir y ejecutar:
echo docker build -t clickup-gantt .
echo docker run -p 8501:8501 -e CLICKUP_API_TOKEN="tu_token" clickup-gantt
echo.
pause
goto fin

:fin
echo.
echo 👋 Gracias por usar el script de despliegue seguro
pause
