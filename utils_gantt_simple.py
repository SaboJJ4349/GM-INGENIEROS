"""
Utilidades simplificadas para Streamlit Cloud
Versión limpia sin dependencias externas
"""
import json
import os

def dummy_function():
    """Función dummy para mantener compatibilidad"""
    pass

# Funciones básicas que podrían ser necesarias
def verificar_datos_existentes():
    """Verifica si existen datos locales"""
    return os.path.exists("tareas_sin_subtareas.json")

def procesar_datos_basico(datos):
    """Procesa datos básicos"""
    return datos

# Mantener compatibilidad pero sin funcionalidad compleja
def get_clickup_config():
    """Función de compatibilidad"""
    return {
        'api_token': None,
        'space_id': '90111892233',
        'environment': 'demo'
    }
