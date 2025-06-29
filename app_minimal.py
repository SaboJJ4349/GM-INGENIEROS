import streamlit as st
import json
import os

# Configuración básica
st.set_page_config(page_title="ClickUp Dashboard", page_icon="📊")

# Título
st.title("📊 ClickUp Dashboard")

# Función ultra-simple para cargar datos
def cargar_datos_simple():
    archivo = "tareas_sin_subtareas.json"
    
    if os.path.exists(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f), True
        except:
            pass
    
    # Datos de emergencia
    return {
        "Demo": {
            "Proyecto": {
                "Tareas": {
                    "pendiente": [{"nombre": "Tarea Demo", "estado": "pendiente"}],
                    "completado": [{"nombre": "Tarea Completada", "estado": "completado"}]
                }
            }
        }
    }, False

# Cargar datos
datos, es_real = cargar_datos_simple()

# Mostrar estado
if es_real:
    st.success("✅ Datos reales cargados")
else:
    st.info("🧪 Modo demo - datos de ejemplo")

# Mostrar configuración
with st.sidebar:
    st.markdown("### Configuración")
    
    try:
        if 'clickup' in st.secrets:
            st.write("**API:** ✅ Configurado")
        else:
            st.write("**API:** ❌ No configurado")
    except:
        st.write("**API:** ❌ No configurado")

# Contar tareas
total = 0
for area in datos.values():
    for carpeta in area.values():
        for lista in carpeta.values():
            for estado in lista.values():
                total += len(estado) if isinstance(estado, list) else 0

# Mostrar métricas
st.metric("Total Tareas", total)

# Mostrar datos
st.json(datos)

# Instrucciones
st.markdown("""
### 🔧 Para usar datos reales:

Configura en **Settings > Secrets**:
```toml
[clickup]
api_token = "tu_token"
space_id = "tu_space_id"
```
""")

st.markdown("*Aplicación funcionando correctamente* ✅")
