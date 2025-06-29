import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import numpy as np
import os

# Importar configuración simple
try:
    from simple_config import get_simple_config, is_demo_mode, get_masked_token
except ImportError:
    # Fallback si no se puede importar
    def get_simple_config():
        return {'api_token': None, 'space_id': '90111892233', 'environment': 'demo', 'debug_mode': True}
    def is_demo_mode(config):
        return True
    def get_masked_token(token):
        return "***"

# Configuración de la página
st.set_page_config(
    page_title="📊 Diagrama de Gantt - Gestión de Tareas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Diagrama de Gantt - Gestión de Tareas ClickUp")

# Obtener configuración
config = get_simple_config()

# Mostrar estado
with st.sidebar:
    st.markdown("### 🔧 Estado de Configuración")
    
    if is_demo_mode(config):
        st.info("🧪 Modo DEMO - Datos de ejemplo")
        st.write("**API Token:** ❌ No configurado")
        st.write("**Space ID:** ✅ Valor por defecto")
    else:
        st.success("🚀 Modo PRODUCCIÓN")
        st.write("**API Token:** ✅ Configurado")
        st.write(f"**Token (masked):** {get_masked_token(config['api_token'])}")
        st.write("**Space ID:** ✅ Configurado")

# Verificar si hay datos
datos_file = "tareas_sin_subtareas.json"
if os.path.exists(datos_file):
    st.success("✅ Datos disponibles")
    
    try:
        with open(datos_file, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        st.json(datos, expanded=False)
        
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        
else:
    st.info("ℹ️ No hay datos disponibles. Generando datos de ejemplo...")
    
    # Datos de ejemplo
    datos_ejemplo = {
        "Administración y Sistemas": {
            "Proyecto Demo": {
                "Tareas de Ejemplo": {
                    "pendiente": [
                        {
                            "nombre": "Tarea de ejemplo 1",
                            "estado": "pendiente",
                            "asignados": ["Usuario Demo"],
                            "fecha_inicio": "01/07/25",
                            "fecha_limite": "15/07/25",
                            "prioridad": "normal"
                        }
                    ],
                    "en progreso": [
                        {
                            "nombre": "Tarea de ejemplo 2",
                            "estado": "en progreso",
                            "asignados": ["Usuario Demo"],
                            "fecha_inicio": "20/06/25",
                            "fecha_limite": "10/07/25",
                            "prioridad": "high"
                        }
                    ]
                }
            }
        }
    }
    
    st.json(datos_ejemplo, expanded=False)

# Información de configuración para Streamlit Cloud
st.markdown("---")
st.markdown("### 🔧 Configuración para Streamlit Cloud")

st.markdown("""
Para usar datos reales, configura en **Settings > Secrets**:

```toml
[clickup]
api_token = "tu_token_aqui"
space_id = "tu_space_id_aqui"
```
""")

st.markdown("📖 [Ver guía completa de configuración](https://github.com/tu-repo/README.md)")

# Pie de página
st.markdown("---")
st.markdown("*🔐 Aplicación ejecutándose de manera segura*")
