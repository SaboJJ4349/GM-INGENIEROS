Actualizado
# ClickUp Gantt Viewer 📊

Una aplicación web moderna para visualizar tareas de ClickUp en formato de diagrama de Gantt interactivo.

## 🌐 Demo en Vivo
[Ver aplicación en Streamlit Cloud](https://tu-app-url.streamlit.app)

## ✨ Características
- 📈 **Diagrama de Gantt interactivo** con Plotly
- 🔍 **Filtros avanzados**: Estado, Área, Prioridad, Carpeta, Lista, Asignados, Fechas
- 📊 **Dashboard con métricas** y gráficos
- 🔒 **Seguro**: Tokens protegidos, sin datos sensibles en código
- 🚀 **Listo para la nube**: Compatible con Streamlit Cloud

## 🚀 Despliegue Rápido

### Opción 1: Usar con datos de ejemplo
La aplicación funciona inmediatamente con datos de ejemplo incluidos.

### Opción 2: Conectar con ClickUp
1. Obtén tu token de ClickUp desde [app.clickup.com/settings/integrations](https://app.clickup.com/settings/integrations)
2. Encuentra tu Team ID en la URL de ClickUp
3. Configura los secrets en Streamlit Cloud:
   ```toml
   [clickup]
   token = "tu_token_aqui"
   team_id = "tu_team_id_aqui"
   ```

## 🛠️ Desarrollo Local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📋 Estructura del Proyecto
- `streamlit_app.py` - Aplicación principal
- `utils_gantt.py` - Utilidades para procesamiento de datos
- `tareas_sin_subtareas.json` - Datos de ejemplo
- `requirements.txt` - Dependencias
- `runtime.txt` - Versión de Python

## 🔧 Configuración
La aplicación soporta configuración mediante:
- Streamlit secrets (recomendado para producción)
- Variables de entorno
- Datos de ejemplo (modo demo)

## 📝 Licencia
Este proyecto está bajo la Licencia MIT.
