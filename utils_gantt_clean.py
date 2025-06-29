"""
Utilidades simplificadas para el procesamiento de datos de Gantt
Compatible con Streamlit Cloud - Sin dependencias externas
"""

import json
import os
import requests
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

def obtener_configuracion_clickup():
    """Obtiene configuración de ClickUp de manera segura para Streamlit Cloud"""
    config = {
        'api_token': None,
        'space_id': '90111892233',
        'environment': 'demo'
    }
    
    # Intentar desde Streamlit secrets
    try:
        if hasattr(st, 'secrets') and 'clickup' in st.secrets:
            config['api_token'] = st.secrets.clickup.get('api_token')
            config['space_id'] = st.secrets.clickup.get('space_id', '90111892233')
            config['environment'] = 'production'
    except:
        pass
    
    # Intentar desde variables de entorno
    try:
        api_token = os.environ.get('CLICKUP_API_TOKEN')
        if api_token:
            config['api_token'] = api_token
            config['space_id'] = os.environ.get('CLICKUP_SPACE_ID', '90111892233')
            config['environment'] = 'production'
    except:
        pass
    
    return config

def verificar_archivo_datos():
    """Verifica si existe el archivo de datos local"""
    return os.path.exists("tareas_sin_subtareas.json")

def cargar_datos_desde_archivo():
    """Carga datos desde archivo JSON local"""
    try:
        with open("tareas_sin_subtareas.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return None

def obtener_datos_clickup(config):
    """Obtiene datos desde la API de ClickUp"""
    if not config.get('api_token'):
        return None
    
    try:
        headers = {
            'Authorization': config['api_token'],
            'Content-Type': 'application/json'
        }
        
        # Obtener tareas del space
        url = f"https://api.clickup.com/api/v2/space/{config['space_id']}/task"
        
        params = {
            'archived': 'false',
            'page': 0,
            'order_by': 'created',
            'reverse': 'true',
            'subtasks': 'true',
            'include_closed': 'true'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error API ClickUp: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error conectando con ClickUp: {e}")
        return None

def procesar_datos_clickup(data):
    """Procesa datos de ClickUp al formato esperado"""
    if not data or 'tasks' not in data:
        return None
    
    # Estructura simplificada
    resultado = {}
    
    for task in data['tasks']:
        # Organizar por carpeta/lista
        carpeta = task.get('folder', {}).get('name', 'Sin Carpeta')
        lista = task.get('list', {}).get('name', 'Sin Lista')
        estado = task.get('status', {}).get('status', 'pendiente').lower()
        
        # Inicializar estructura
        if carpeta not in resultado:
            resultado[carpeta] = {}
        if lista not in resultado[carpeta]:
            resultado[carpeta][lista] = {}
        if estado not in resultado[carpeta][lista]:
            resultado[carpeta][lista][estado] = []
        
        # Procesar fechas
        fecha_inicio = 'N/A'
        fecha_limite = 'N/A'
        
        if task.get('start_date'):
            try:
                fecha_inicio = datetime.fromtimestamp(int(task['start_date'])/1000).strftime('%d/%m/%y')
            except:
                pass
        
        if task.get('due_date'):
            try:
                fecha_limite = datetime.fromtimestamp(int(task['due_date'])/1000).strftime('%d/%m/%y')
            except:
                pass
        
        # Procesar asignados
        asignados = []
        for assignee in task.get('assignees', []):
            asignados.append(assignee.get('username', 'Sin nombre'))
        
        # Crear tarea procesada
        tarea_procesada = {
            'nombre': task.get('name', 'Sin nombre'),
            'estado': estado,
            'asignados': asignados,
            'fecha_inicio': fecha_inicio,
            'fecha_limite': fecha_limite,
            'prioridad': task.get('priority', {}).get('priority', 'normal').lower()
        }
        
        resultado[carpeta][lista][estado].append(tarea_procesada)
    
    return resultado

def guardar_datos_procesados(datos, archivo='tareas_sin_subtareas.json'):
    """Guarda datos procesados en archivo JSON"""
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando datos: {e}")
        return False

def validar_estructura_datos(datos):
    """Valida que los datos tengan la estructura esperada"""
    if not isinstance(datos, dict):
        return False
    
    for area, carpetas in datos.items():
        if not isinstance(carpetas, dict):
            return False
        for carpeta, listas in carpetas.items():
            if not isinstance(listas, dict):
                return False
            for lista, estados in listas.items():
                if not isinstance(estados, dict):
                    return False
                for estado, tareas in estados.items():
                    if not isinstance(tareas, list):
                        return False
    
    return True

def obtener_estadisticas_datos(datos):
    """Obtiene estadísticas básicas de los datos"""
    if not datos:
        return {}
    
    stats = {
        'total_areas': len(datos),
        'total_carpetas': 0,
        'total_listas': 0,
        'total_tareas': 0,
        'tareas_por_estado': {}
    }
    
    for area, carpetas in datos.items():
        stats['total_carpetas'] += len(carpetas)
        for carpeta, listas in carpetas.items():
            stats['total_listas'] += len(listas)
            for lista, estados in listas.items():
                for estado, tareas in estados.items():
                    stats['total_tareas'] += len(tareas)
                    if estado not in stats['tareas_por_estado']:
                        stats['tareas_por_estado'][estado] = 0
                    stats['tareas_por_estado'][estado] += len(tareas)
    
    return stats
