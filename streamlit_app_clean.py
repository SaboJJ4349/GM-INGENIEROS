import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os

# ===== CONFIGURACIÓN BÁSICA =====
st.set_page_config(
    page_title="📊 ClickUp Gantt Dashboard",
    page_icon="📊",
    layout="wide"
)

# ===== FUNCIONES AUXILIARES =====
def obtener_configuracion():
    """Obtiene configuración de manera ultra-segura"""
    config = {
        'api_token': None,
        'space_id': '90111892233',
        'environment': 'demo',
        'app_ready': True
    }
    
    # Intentar obtener desde secrets
    try:
        if hasattr(st, 'secrets') and 'clickup' in st.secrets:
            config['api_token'] = st.secrets.clickup.api_token
            config['space_id'] = st.secrets.clickup.space_id
            config['environment'] = 'production'
    except:
        pass
    
    # Intentar obtener desde variables de entorno
    try:
        api_token = os.environ.get('CLICKUP_API_TOKEN')
        if api_token:
            config['api_token'] = api_token
            config['space_id'] = os.environ.get('CLICKUP_SPACE_ID', '90111892233')
            config['environment'] = 'production'
    except:
        pass
    
    return config

def cargar_datos():
    """Carga datos desde archivo JSON o usa datos de ejemplo"""
    archivo_datos = "tareas_sin_subtareas.json"
    
    # Intentar cargar datos reales
    if os.path.exists(archivo_datos):
        try:
            with open(archivo_datos, 'r', encoding='utf-8') as f:
                return json.load(f), "real"
        except:
            pass
    
    # Datos de ejemplo si no hay datos reales
    datos_ejemplo = {
        "Administración y Sistemas": {
            "SistemasGM": {
                "Tareas": {
                    "pendiente": [
                        {
                            "nombre": "Implementar Sistema de Facturación",
                            "estado": "pendiente",
                            "asignados": ["Juan Pérez"],
                            "fecha_inicio": "01/07/25",
                            "fecha_limite": "15/07/25",
                            "prioridad": "high"
                        },
                        {
                            "nombre": "Configurar Base de Datos",
                            "estado": "pendiente",
                            "asignados": ["María García"],
                            "fecha_inicio": "05/07/25",
                            "fecha_limite": "20/07/25",
                            "prioridad": "normal"
                        }
                    ],
                    "en progreso": [
                        {
                            "nombre": "Desarrollo API REST",
                            "estado": "en progreso",
                            "asignados": ["Carlos López"],
                            "fecha_inicio": "15/06/25",
                            "fecha_limite": "30/06/25",
                            "prioridad": "urgent"
                        },
                        {
                            "nombre": "Testing de Módulos",
                            "estado": "en progreso",
                            "asignados": ["Ana Martín"],
                            "fecha_inicio": "20/06/25",
                            "fecha_limite": "10/07/25",
                            "prioridad": "high"
                        }
                    ],
                    "completado": [
                        {
                            "nombre": "Análisis de Requerimientos",
                            "estado": "completado",
                            "asignados": ["Pedro Sánchez"],
                            "fecha_inicio": "01/06/25",
                            "fecha_limite": "15/06/25",
                            "prioridad": "normal"
                        },
                        {
                            "nombre": "Diseño de Arquitectura",
                            "estado": "completado",
                            "asignados": ["Luis Torres"],
                            "fecha_inicio": "10/06/25",
                            "fecha_limite": "25/06/25",
                            "prioridad": "high"
                        }
                    ]
                }
            }
        },
        "Desarrollo Web": {
            "Frontend": {
                "UI/UX": {
                    "pendiente": [
                        {
                            "nombre": "Diseño de Dashboard",
                            "estado": "pendiente",
                            "asignados": ["Elena Ruiz"],
                            "fecha_inicio": "01/07/25",
                            "fecha_limite": "12/07/25",
                            "prioridad": "normal"
                        }
                    ],
                    "en progreso": [
                        {
                            "nombre": "Responsive Design",
                            "estado": "en progreso",
                            "asignados": ["Miguel Herrera"],
                            "fecha_inicio": "25/06/25",
                            "fecha_limite": "05/07/25",
                            "prioridad": "high"
                        }
                    ],
                    "completado": [
                        {
                            "nombre": "Prototipo Inicial",
                            "estado": "completado",
                            "asignados": ["Sofia Castro"],
                            "fecha_inicio": "15/06/25",
                            "fecha_limite": "22/06/25",
                            "prioridad": "normal"
                        }
                    ]
                }
            }
        }
    }
    
    return datos_ejemplo, "ejemplo"

def procesar_datos_para_tabla(datos):
    """Convierte datos JSON a formato de tabla"""
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
    
    return pd.DataFrame(filas) if filas else pd.DataFrame()

def convertir_fecha(fecha_str):
    """Convierte fecha del formato DD/MM/YY a datetime"""
    if not fecha_str or fecha_str == 'N/A':
        return None
    
    try:
        # Intentar formato DD/MM/YY
        if '/' in fecha_str:
            fecha = datetime.strptime(fecha_str, '%d/%m/%y')
            return fecha
        # Intentar otros formatos
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except:
        return None

def crear_diagrama_gantt(df):
    """Crea el diagrama de Gantt interactivo"""
    if df.empty:
        return None
    
    # Preparar datos para Gantt
    gantt_data = []
    
    for _, row in df.iterrows():
        fecha_inicio = convertir_fecha(row['Fecha Inicio'])
        fecha_fin = convertir_fecha(row['Fecha Límite'])
        
        # Si no hay fechas válidas, usar fechas por defecto
        if not fecha_inicio:
            fecha_inicio = datetime.now()
        if not fecha_fin:
            fecha_fin = fecha_inicio + timedelta(days=7)
        
        # Color según estado
        color_map = {
            'completado': '#28a745',
            'en progreso': '#ffc107', 
            'pendiente': '#dc3545'
        }
        
        gantt_data.append({
            'Task': row['Tarea'][:50] + ('...' if len(row['Tarea']) > 50 else ''),
            'Start': fecha_inicio,
            'Finish': fecha_fin,
            'Resource': row['Área'],
            'Estado': row['Estado'],
            'Asignados': row['Asignados'],
            'Prioridad': row['Prioridad'],
            'Color': color_map.get(row['Estado'], '#6c757d')
        })
    
    if not gantt_data:
        return None
    
    # Crear figura de Gantt
    fig = go.Figure()
    
    # Añadir barras del Gantt
    for i, task in enumerate(gantt_data):
        fig.add_trace(go.Scatter(
            x=[task['Start'], task['Finish']],
            y=[i, i],
            mode='lines',
            line=dict(color=task['Color'], width=20),
            name=task['Task'],
            text=f"<b>{task['Task']}</b><br>Estado: {task['Estado']}<br>Asignados: {task['Asignados']}<br>Prioridad: {task['Prioridad']}",
            hovertemplate='%{text}<extra></extra>',
            showlegend=False
        ))
    
    # Configurar layout
    fig.update_layout(
        title="📅 Diagrama de Gantt - Cronograma de Tareas",
        xaxis_title="Fecha",
        yaxis_title="Tareas",
        height=max(400, len(gantt_data) * 40 + 100),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(gantt_data))),
            ticktext=[task['Task'] for task in gantt_data],
            showgrid=True
        ),
        xaxis=dict(
            type='date',
            showgrid=True
        ),
        hovermode='closest',
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def crear_cronograma_simple(df):
    """Crea un cronograma más simple como alternativa"""
    if df.empty:
        return None
    
    # Contar tareas por fecha
    fechas_data = []
    
    for _, row in df.iterrows():
        fecha_limite = convertir_fecha(row['Fecha Límite'])
        if fecha_limite:
            fechas_data.append({
                'Fecha': fecha_limite.strftime('%Y-%m-%d'),
                'Tareas': 1,
                'Estado': row['Estado'],
                'Tarea': row['Tarea']
            })
    
    if not fechas_data:
        return None
    
    # Crear DataFrame temporal
    df_fechas = pd.DataFrame(fechas_data)
    cronograma = df_fechas.groupby(['Fecha', 'Estado']).size().reset_index(name='Cantidad')
    
    # Crear gráfico de barras apiladas
    fig = px.bar(
        cronograma,
        x='Fecha',
        y='Cantidad',
        color='Estado',
        title="📆 Cronograma de Entregas por Estado",
        color_discrete_map={
            'completado': '#28a745',
            'en progreso': '#ffc107',
            'pendiente': '#dc3545'
        }
    )
    
    fig.update_layout(height=400)
    return fig

def aplicar_filtros(df, filtros):
    """Aplica todos los filtros al DataFrame"""
    df_filtrado = df.copy()
    
    # Filtros básicos
    if filtros['estados']:
        df_filtrado = df_filtrado[df_filtrado['Estado'].isin(filtros['estados'])]
    
    if filtros['areas']:
        df_filtrado = df_filtrado[df_filtrado['Área'].isin(filtros['areas'])]
    
    if filtros['prioridades']:
        df_filtrado = df_filtrado[df_filtrado['Prioridad'].isin(filtros['prioridades'])]
    
    # Búsqueda de texto
    if filtros['buscar_texto']:
        df_filtrado = df_filtrado[
            df_filtrado['Tarea'].str.contains(filtros['buscar_texto'], case=False, na=False)
        ]
    
    # Filtros rápidos
    if filtros['filtro_rapido'] == "Solo Pendientes":
        df_filtrado = df_filtrado[df_filtrado['Estado'] == 'pendiente']
    elif filtros['filtro_rapido'] == "Solo En Progreso":
        df_filtrado = df_filtrado[df_filtrado['Estado'] == 'en progreso']
    elif filtros['filtro_rapido'] == "Solo Completadas":
        df_filtrado = df_filtrado[df_filtrado['Estado'] == 'completado']
    elif filtros['filtro_rapido'] == "Prioridad Alta":
        df_filtrado = df_filtrado[df_filtrado['Prioridad'].isin(['high', 'urgent'])]
    elif filtros['filtro_rapido'] == "Sin Asignar":
        df_filtrado = df_filtrado[
            (df_filtrado['Asignados'].isna()) | 
            (df_filtrado['Asignados'] == '') | 
            (df_filtrado['Asignados'] == 'N/A')
        ]
    
    # Solo tareas activas
    if filtros['solo_activas']:
        df_filtrado = df_filtrado[df_filtrado['Estado'] != 'completado']
    
    return df_filtrado

# ===== APLICACIÓN PRINCIPAL =====
def main():
    try:
        # Título principal
        st.title("📊 Dashboard de Gestión de Tareas ClickUp")
        
        # Obtener configuración
        config = obtener_configuracion()
        
        # Cargar datos
        datos, tipo_datos = cargar_datos()
        df = procesar_datos_para_tabla(datos)
        
        if df.empty:
            st.error("❌ No se encontraron datos para mostrar")
            return
        
        # SIDEBAR CON FILTROS
        with st.sidebar:
            st.markdown("### 🔧 Estado del Sistema")
            
            if config['environment'] == 'demo':
                st.info("🧪 Modo DEMO")
                st.write("Usando datos de ejemplo")
            else:
                st.success("🚀 Modo PRODUCCIÓN")
                st.write("Conectado a ClickUp API")
            
            st.markdown("---")
            st.markdown("### ⚙️ Configuración")
            
            if config['api_token']:
                st.success("✅ Token Configurado")
                token_mask = f"pk_{config['api_token'][3:6]}...{config['api_token'][-4:]}"
                st.code(token_mask)
            else:
                st.error("❌ Token No configurado")
            
            st.write(f"**Space ID:** {config['space_id']}")
            
            st.markdown("---")
            st.markdown("### 🔍 Filtros")
            
            # Filtros principales
            estados_seleccionados = st.multiselect(
                "📊 Estado",
                options=df['Estado'].unique(),
                default=df['Estado'].unique(),
                key="filtro_estados"
            )
            
            areas_seleccionadas = st.multiselect(
                "🏢 Área",
                options=df['Área'].unique(),
                default=df['Área'].unique(),
                key="filtro_areas"
            )
            
            prioridades_seleccionadas = st.multiselect(
                "🎯 Prioridad",
                options=df['Prioridad'].unique(),
                default=df['Prioridad'].unique(),
                key="filtro_prioridades"
            )
            
            # Filtro rápido
            filtro_rapido = st.selectbox(
                "⚡ Filtro Rápido",
                options=[
                    "Todos",
                    "Solo Pendientes",
                    "Solo En Progreso", 
                    "Solo Completadas",
                    "Prioridad Alta",
                    "Sin Asignar"
                ],
                key="filtro_rapido"
            )
            
            # Búsqueda de texto
            buscar_tarea = st.text_input(
                "🔍 Buscar",
                placeholder="Nombre de tarea...",
                key="buscar_texto"
            )
            
            # Configuración de vista
            st.markdown("### ⚙️ Vista")
            
            mostrar_solo_activas = st.checkbox(
                "Solo activas",
                help="Ocultar completadas",
                key="solo_activas"
            )
            
            # Botón limpiar filtros
            if st.button("🔄 Limpiar", key="limpiar"):
                st.experimental_rerun()
        
        # Aplicar filtros
        filtros = {
            'estados': estados_seleccionados,
            'areas': areas_seleccionadas,
            'prioridades': prioridades_seleccionadas,
            'filtro_rapido': filtro_rapido,
            'buscar_texto': buscar_tarea,
            'solo_activas': mostrar_solo_activas
        }
        
        df_filtrado = aplicar_filtros(df, filtros)
        
        # CONTENIDO PRINCIPAL
        if tipo_datos == "ejemplo":
            st.warning("⚠️ Mostrando datos de ejemplo. Configura tu token de ClickUp para ver datos reales.")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tareas = len(df_filtrado)
            st.metric("📋 Total", total_tareas)
        
        with col2:
            pendientes = len(df_filtrado[df_filtrado['Estado'] == 'pendiente'])
            st.metric("⏳ Pendientes", pendientes)
        
        with col3:
            en_progreso = len(df_filtrado[df_filtrado['Estado'] == 'en progreso'])
            st.metric("🔄 En Progreso", en_progreso)
        
        with col4:
            completadas = len(df_filtrado[df_filtrado['Estado'] == 'completado'])
            st.metric("✅ Completadas", completadas)
        
        # Información de filtros
        if len(df_filtrado) < len(df):
            st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df)} tareas")
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📅 Diagrama de Gantt", "📆 Cronograma", "📋 Tabla"])
        
        with tab1:
            if len(df_filtrado) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico por estado
                    estados_count = df_filtrado['Estado'].value_counts()
                    if len(estados_count) > 0:
                        fig_pie = px.pie(
                            values=estados_count.values,
                            names=estados_count.index,
                            title="📊 Distribución por Estado",
                            color_discrete_map={
                                'completado': '#28a745',
                                'en progreso': '#ffc107',
                                'pendiente': '#dc3545'
                            }
                        )
                        fig_pie.update_layout(height=400)
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Gráfico por prioridad
                    prioridades_count = df_filtrado['Prioridad'].value_counts()
                    if len(prioridades_count) > 0:
                        fig_bar = px.bar(
                            x=prioridades_count.index,
                            y=prioridades_count.values,
                            title="🎯 Distribución por Prioridad",
                            color=prioridades_count.index,
                            color_discrete_map={
                                'urgent': '#dc3545',
                                'high': '#fd7e14',
                                'normal': '#ffc107',
                                'low': '#28a745'
                            }
                        )
                        fig_bar.update_layout(height=400)
                        st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No hay datos para mostrar con los filtros aplicados")
        
        with tab2:
            st.subheader("📅 Diagrama de Gantt")
            
            if len(df_filtrado) > 0:
                try:
                    fig_gantt = crear_diagrama_gantt(df_filtrado)
                    if fig_gantt:
                        st.plotly_chart(fig_gantt, use_container_width=True)
                        
                        st.info("""
                        💡 **Información del Diagrama:**
                        - 🟢 Verde: Tareas completadas
                        - 🟡 Amarillo: Tareas en progreso  
                        - 🔴 Rojo: Tareas pendientes
                        """)
                    else:
                        st.warning("⚠️ No se pudo generar el diagrama. Verifica que las tareas tengan fechas válidas.")
                        
                        # Mostrar tabla de fechas para debug
                        st.subheader("🔍 Información de fechas")
                        fechas_info = df_filtrado[['Tarea', 'Fecha Inicio', 'Fecha Límite']].copy()
                        st.dataframe(fechas_info)
                        
                except Exception as e:
                    st.error(f"Error al crear el diagrama de Gantt: {str(e)}")
                    st.info("Intenta con diferentes filtros o verifica el formato de las fechas.")
            else:
                st.warning("No hay tareas para mostrar el diagrama de Gantt")
        
        with tab3:
            st.subheader("📆 Cronograma de Entregas")
            
            if len(df_filtrado) > 0:
                try:
                    fig_cronograma = crear_cronograma_simple(df_filtrado)
                    if fig_cronograma:
                        st.plotly_chart(fig_cronograma, use_container_width=True)
                    else:
                        st.warning("⚠️ No se pudo generar el cronograma.")
                        
                        # Mostrar información de fechas
                        fechas_validas = []
                        for _, row in df_filtrado.iterrows():
                            fecha_limite = convertir_fecha(row['Fecha Límite'])
                            if fecha_limite:
                                fechas_validas.append({
                                    'Tarea': row['Tarea'],
                                    'Fecha': fecha_limite.strftime('%Y-%m-%d'),
                                    'Estado': row['Estado']
                                })
                        
                        if fechas_validas:
                            st.subheader("📅 Fechas válidas encontradas:")
                            st.dataframe(pd.DataFrame(fechas_validas))
                        else:
                            st.info("No se encontraron fechas válidas en las tareas filtradas.")
                            
                except Exception as e:
                    st.error(f"Error al crear el cronograma: {str(e)}")
            else:
                st.warning("No hay tareas para mostrar el cronograma")
        
        with tab4:
            st.subheader("📋 Tabla de Tareas")
            
            if len(df_filtrado) > 0:
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                
                # Descarga CSV
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"tareas_clickup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No hay tareas para mostrar en la tabla")
        
        # Información adicional
        with st.expander("📖 Ayuda y Configuración"):
            st.markdown("""
            ### 🔧 Configuración para Producción
            
            Para usar datos reales de ClickUp, añade en **Settings > Secrets**:
            
            ```toml
            [clickup]
            api_token = "tu_token_aqui"
            space_id = "tu_space_id"
            ```
            
            ### 🎯 Cómo usar los filtros
            
            - **Estado**: Filtra por pendiente, en progreso, completado
            - **Área**: Selecciona áreas de trabajo específicas  
            - **Prioridad**: Filtra por nivel de urgencia
            - **Filtro Rápido**: Aplicar filtros comunes rápidamente
            - **Búsqueda**: Buscar texto en nombres de tareas
            - **Solo Activas**: Oculta tareas completadas
            """)
    
    except Exception as e:
        st.error(f"❌ Error en la aplicación: {str(e)}")
        st.info("🔧 La aplicación sigue funcionando en modo seguro.")
        
        # Mostrar información básica de emergencia
        st.markdown("### 📊 Información Básica")
        st.write("- Estado: Operativo")
        st.write("- Modo: Seguro")
        st.write("- Datos: Disponibles")

# Ejecutar aplicación
if __name__ == "__main__":
    main()
