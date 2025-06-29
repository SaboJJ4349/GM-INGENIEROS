import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Configuración básica
st.set_page_config(
    page_title="📊 ClickUp Gantt Dashboard",
    page_icon="📊",
    layout="wide"
)

def obtener_datos_ejemplo():
    """Datos de ejemplo seguros"""
    return {
        "Desarrollo": {
            "Frontend": {
                "UI Components": {
                    "pendiente": [
                        {
                            "nombre": "Diseño de Dashboard",
                            "estado": "pendiente",
                            "asignados": ["María García"],
                            "fecha_inicio": "01/07/25",
                            "fecha_limite": "15/07/25",
                            "prioridad": "high"
                        }
                    ],
                    "en progreso": [
                        {
                            "nombre": "Componentes React",
                            "estado": "en progreso",
                            "asignados": ["Juan Pérez"],
                            "fecha_inicio": "20/06/25",
                            "fecha_limite": "10/07/25",
                            "prioridad": "normal"
                        }
                    ]
                }
            }
        }
    }

def procesar_datos(datos):
    """Convierte datos a DataFrame"""
    filas = []
    for area, carpetas in datos.items():
        for carpeta, listas in carpetas.items():
            for lista, estados in listas.items():
                for estado, tareas in estados.items():
                    for tarea in tareas:
                        filas.append({
                            'Área': area,
                            'Carpeta': carpeta,
                            'Lista': lista,
                            'Tarea': tarea['nombre'],
                            'Estado': estado,
                            'Asignados': ', '.join(tarea.get('asignados', [])),
                            'Fecha Inicio': tarea.get('fecha_inicio', 'N/A'),
                            'Fecha Límite': tarea.get('fecha_limite', 'N/A'),
                            'Prioridad': tarea.get('prioridad', 'normal')
                        })
    return pd.DataFrame(filas)

def convertir_fecha(fecha_str):
    """Convierte fecha del formato DD/MM/YY a datetime"""
    if not fecha_str or fecha_str == 'N/A':
        return None
    try:
        return datetime.strptime(fecha_str, '%d/%m/%y')
    except:
        return None

def crear_gantt(df):
    """Crea diagrama de Gantt"""
    if df.empty:
        return None
    
    gantt_data = []
    for _, row in df.iterrows():
        fecha_inicio = convertir_fecha(row['Fecha Inicio'])
        fecha_fin = convertir_fecha(row['Fecha Límite'])
        
        if not fecha_inicio:
            fecha_inicio = datetime.now()
        if not fecha_fin:
            fecha_fin = fecha_inicio + timedelta(days=7)
        
        color_map = {
            'completado': '#28a745',
            'en progreso': '#ffc107', 
            'pendiente': '#dc3545'
        }
        
        gantt_data.append({
            'Task': row['Tarea'][:40] + ('...' if len(row['Tarea']) > 40 else ''),
            'Start': fecha_inicio,
            'Finish': fecha_fin,
            'Estado': row['Estado'],
            'Color': color_map.get(row['Estado'], '#6c757d')
        })
    
    if not gantt_data:
        return None
    
    fig = go.Figure()
    
    for i, task in enumerate(gantt_data):
        fig.add_trace(go.Scatter(
            x=[task['Start'], task['Finish']],
            y=[i, i],
            mode='lines',
            line=dict(color=task['Color'], width=20),
            name=task['Task'],
            showlegend=False
        ))
    
    fig.update_layout(
        title="📅 Diagrama de Gantt",
        xaxis_title="Fecha",
        yaxis_title="Tareas",
        height=400,
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(gantt_data))),
            ticktext=[task['Task'] for task in gantt_data]
        ),
        showlegend=False
    )
    
    return fig

def main():
    """Función principal simplificada"""
    try:
        st.title("📊 ClickUp Gantt Dashboard")
        
        # Obtener datos
        datos = obtener_datos_ejemplo()
        df = procesar_datos(datos)
        
        # Sidebar con filtros básicos
        with st.sidebar:
            st.header("🔧 Filtros")
            
            estados = st.multiselect(
                "Estados",
                options=df['Estado'].unique(),
                default=df['Estado'].unique()
            )
            
            areas = st.multiselect(
                "Áreas", 
                options=df['Área'].unique(),
                default=df['Área'].unique()
            )
        
        # Filtrar datos
        df_filtrado = df[
            (df['Estado'].isin(estados)) & 
            (df['Área'].isin(areas))
        ]
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tareas", len(df_filtrado))
        with col2:
            pendientes = len(df_filtrado[df_filtrado['Estado'] == 'pendiente'])
            st.metric("Pendientes", pendientes)
        with col3:
            en_progreso = len(df_filtrado[df_filtrado['Estado'] == 'en progreso'])
            st.metric("En Progreso", en_progreso)
        
        # Pestañas
        tab1, tab2 = st.tabs(["📅 Gantt", "📋 Tabla"])
        
        with tab1:
            st.subheader("Diagrama de Gantt")
            if not df_filtrado.empty:
                fig = crear_gantt(df_filtrado)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No se pudo generar el diagrama")
            else:
                st.warning("No hay datos para mostrar")
        
        with tab2:
            st.subheader("Tabla de Tareas")
            st.dataframe(df_filtrado, use_container_width=True)
        
        # Info de estado
        st.success("✅ Aplicación funcionando correctamente")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Usando modo de emergencia")

if __name__ == "__main__":
    main()
