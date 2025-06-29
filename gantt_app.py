import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import numpy as np
from config import get_config, validate_config, show_config_status, log_debug
from utils_gantt import (
    actualizar_datos_desde_clickup, 
    verificar_datos_existentes, 
    generar_datos_ejemplo,
    exportar_a_excel,
    calcular_estadisticas_avanzadas
)

# Configuración de la página
st.set_page_config(
    page_title="📊 Diagrama de Gantt - Gestión de Tareas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    /* Mejorar el diseño general */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Estilo del sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Estilo del título principal */
    h1 {
        color: #2C3E50;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Mejorar las métricas */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1rem;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    div[data-testid="metric-container"] > div {
        color: white;
    }
    
    /* Estilo de los botones */
    .stButton button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    /* Estilo de los selectboxes */
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    /* Mejorar las tablas */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Estilo del gráfico de Plotly */
    .plotly-graph-div {
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo de los expanderes */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("📊 Diagrama de Gantt - Gestión de Tareas ClickUp")

# === VALIDACIÓN DE CONFIGURACIÓN SEGURA ===
try:
    config = get_config()
    show_config_status(config)
    
    # Validar configuración antes de continuar
    if not validate_config(config):
        st.stop()
    
    log_debug("Aplicación iniciada correctamente", config)
    
except Exception as e:
    # Si hay algún error en la configuración, usar modo demo
    st.warning("⚠️ Error en configuración, iniciando en modo DEMO")
    config = {
        'api_token': None,
        'space_id': None,
        'environment': 'demo',
        'debug_mode': True
    }

# Verificar estado de los datos
info_datos = verificar_datos_existentes()

# Barra superior con controles
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    if info_datos["existe"]:
        antigüedad = info_datos["horas_antiguedad"]
        if antigüedad < 1:
            st.success(f"✅ Datos actualizados hace {int(antigüedad * 60)} minutos")
        elif antigüedad < 24:
            st.info(f"ℹ️ Datos de hace {int(antigüedad)} horas")
        else:
            st.warning(f"⚠️ Datos de hace {int(antigüedad / 24)} días")
    else:
        st.error("❌ No hay datos disponibles")

with col2:
    if st.button("🔄 Actualizar desde ClickUp"):
        if actualizar_datos_desde_clickup():
            st.rerun()

with col3:
    if st.button("🎯 Datos de Ejemplo"):
        if generar_datos_ejemplo():
            st.success("✅ Datos de ejemplo generados")
            st.rerun()

with col4:
    if st.button("📊 Ver Estadísticas"):
        st.session_state.show_stats = not st.session_state.get('show_stats', False)

st.markdown("---")

@st.cache_data
def cargar_datos():
    """Cargar y procesar los datos del JSON"""
    try:
        with open("tareas_sin_subtareas.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'tareas_sin_subtareas.json'")
        return None

def convertir_fecha(fecha_str):
    """Convertir fecha en formato dd/mm/yy a datetime"""
    if fecha_str and fecha_str.strip():
        try:
            return datetime.strptime(fecha_str, "%d/%m/%y")
        except:
            return None
    return None

def procesar_datos_gantt(data):
    """Procesar datos para el diagrama de Gantt"""
    tareas = []
    
    for carpeta, listas in data["Administración y Sistemas"].items():
        for lista, estados in listas.items():
            for estado, lista_tareas in estados.items():
                for tarea in lista_tareas:
                    fecha_inicio = convertir_fecha(tarea.get("fecha_inicio"))
                    fecha_limite = convertir_fecha(tarea.get("fecha_limite"))
                    
                    # Si no hay fecha de inicio, usar fecha actual menos algunos días según el estado
                    if not fecha_inicio:
                        if estado == "completado":
                            fecha_inicio = datetime.now() - timedelta(days=30)
                        elif estado == "en progreso":
                            fecha_inicio = datetime.now() - timedelta(days=15)
                        else:  # pendiente
                            fecha_inicio = datetime.now()
                    
                    # Si no hay fecha límite, estimar una duración
                    if not fecha_limite:
                        if estado == "completado":
                            fecha_limite = fecha_inicio + timedelta(days=7)
                        else:
                            fecha_limite = fecha_inicio + timedelta(days=14)
                    
                    # Asegurar que fecha_limite >= fecha_inicio
                    if fecha_limite < fecha_inicio:
                        fecha_limite = fecha_inicio + timedelta(days=1)
                    
                    tareas.append({
                        "Tarea": tarea["nombre"][:50] + "..." if len(tarea["nombre"]) > 50 else tarea["nombre"],
                        "Nombre_Completo": tarea["nombre"],
                        "Carpeta": carpeta,
                        "Lista": lista,
                        "Estado": estado.title(),
                        "Asignados": ", ".join(tarea["asignados"]) if tarea["asignados"] else "Sin asignar",
                        "Prioridad": tarea.get("prioridad", "normal").title() if tarea.get("prioridad") else "Normal",
                        "Fecha_Inicio": fecha_inicio,
                        "Fecha_Limite": fecha_limite,
                        "Duracion": (fecha_limite - fecha_inicio).days + 1
                    })
    
    return pd.DataFrame(tareas)

def crear_diagrama_gantt(df_filtrado, escala_temporal="Meses"):
    """Crear diagrama de Gantt moderno y profesional como en la imagen de referencia"""
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados")
        return None
    
    # Paleta de colores moderna y profesional
    colores_estado = {
        "Pendiente": "#FF6B6B",      # Rojo coral vibrante
        "En Progreso": "#4ECDC4",    # Turquesa moderno
        "Completado": "#45B7D1",     # Azul cielo
        "Pausado": "#96CEB4",        # Verde menta
        "Cancelado": "#FECA57"       # Amarillo cálido
    }
    
    # Colores de prioridad para intensidad
    colores_prioridad = {
        "Alta": 1.0,
        "Media": 0.8,
        "Baja": 0.6,
        "Crítica": 1.2
    }
    
    # Crear figura principal
    fig = go.Figure()
    
    # Ordenar tareas por fecha de inicio y prioridad
    df_sorted = df_filtrado.sort_values(['Fecha_Inicio', 'Prioridad'])
    
    # Obtener rango de fechas
    fecha_min = df_sorted['Fecha_Inicio'].min()
    fecha_max = df_sorted['Fecha_Limite'].max()
    
    # Crear barras del diagrama de Gantt
    estados_agregados = set()
    
    for idx, (_, row) in enumerate(df_sorted.iterrows()):
        # Obtener color base y ajustar intensidad por prioridad
        color_base = colores_estado.get(row['Estado'], '#9E9E9E')
        intensidad = colores_prioridad.get(row['Prioridad'], 0.8)
        
        # Calcular altura de la barra (más gruesa para mayor impacto visual)
        altura_barra = 0.6
        
        # Crear etiqueta corta y clara para el eje Y
        etiqueta_y = f"{idx+1:02d}. {row['Tarea'][:35]}{'...' if len(row['Tarea']) > 35 else ''}"
        
        # Agregar la barra del Gantt
        fig.add_trace(go.Bar(
            x=[row['Duracion']],
            y=[etiqueta_y],
            base=[row['Fecha_Inicio']],
            orientation='h',
            name=row['Estado'],
            marker=dict(
                color=color_base,
                opacity=intensidad,
                line=dict(color='rgba(255,255,255,0.8)', width=2)
            ),
            showlegend=row['Estado'] not in estados_agregados,
            text=f"📋 {row['Asignados'][:15]}{'...' if len(row['Asignados']) > 15 else ''}",
            textposition='inside',
            textfont=dict(
                color='white', 
                size=9, 
                family="Segoe UI, Arial"
            ),
            width=altura_barra,
            hovertemplate=f"<b>🎯 {row['Tarea']}</b><br>" +
                         f"📊 Estado: <b>{row['Estado']}</b><br>" +
                         f"📅 Inicio: <b>{row['Fecha_Inicio'].strftime('%d/%m/%Y')}</b><br>" +
                         f"🏁 Fin: <b>{row['Fecha_Limite'].strftime('%d/%m/%Y')}</b><br>" +
                         f"⏱️ Duración: <b>{row['Duracion']} días</b><br>" +
                         f"👤 Asignados: <b>{row['Asignados']}</b><br>" +
                         f"⚡ Prioridad: <b>{row['Prioridad']}</b><br>" +
                         f"📁 Carpeta: <b>{row['Carpeta']}</b><br>" +
                         "<extra></extra>"
        ))
        
        estados_agregados.add(row['Estado'])
    
    # Configurar el fondo y separadores según la escala temporal
    configurar_fondo_temporal(fig, fecha_min, fecha_max, escala_temporal)
    
    # Layout moderno y profesional
    fig.update_layout(
        title={
            'text': f"📅 Cronograma del Proyecto - Vista por {escala_temporal}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 24, 
                'family': 'Segoe UI, Arial Black', 
                'color': '#2C3E50'
            },
            'pad': {'t': 20}
        },
        height=max(600, len(df_sorted) * 45 + 200),
        margin=dict(l=280, r=100, t=120, b=80),
        plot_bgcolor='#FAFBFC',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12, family="Segoe UI"),
            bordercolor="#E1E8ED",
            borderwidth=2,
            bgcolor="rgba(255,255,255,0.95)",
            itemsizing="constant",
            itemwidth=30
        ),
        font=dict(family="Segoe UI, Arial", size=11),
        hovermode='closest',
        bargap=0.3,
        bargroupgap=0.1
    )
    
    # Configurar ejes con estilo moderno
    configurar_ejes(fig, escala_temporal, fecha_min, fecha_max)
    
    # Agregar línea de "HOY" con estilo destacado
    agregar_linea_hoy(fig, fecha_min, fecha_max)
    
    # Agregar indicadores de progreso visual si es necesario
    if escala_temporal == "Meses":
        agregar_indicadores_mensuales(fig, fecha_min, fecha_max)
    
    return fig


def configurar_fondo_temporal(fig, fecha_min, fecha_max, escala_temporal):
    """Configurar el fondo según la escala temporal seleccionada"""
    if escala_temporal == "Meses":
        # Colores suaves alternados para meses
        colores_meses = ['#E3F2FD', '#F3E5F5', '#E8F5E8', '#FFF3E0', '#FCE4EC', '#E0F2F1']
        
        current_date = fecha_min.replace(day=1)
        mes_idx = 0
        
        while current_date <= fecha_max:
            # Calcular el siguiente mes
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1)
            
            # Agregar fondo alternado para cada mes
            fig.add_vrect(
                x0=current_date,
                x1=min(next_month, fecha_max),
                fillcolor=colores_meses[mes_idx % len(colores_meses)],
                opacity=0.3,
                layer="below",
                line_width=0
            )
            
            current_date = next_month
            mes_idx += 1
    
    elif escala_temporal == "Semanas":
        # Rayas verticales suaves para semanas
        current_date = fecha_min
        while current_date <= fecha_max:
            fig.add_vline(
                x=current_date,
                line_width=1,
                line_color="#E1E8ED",
                opacity=0.5,
                line_dash="dot"
            )
            current_date += timedelta(weeks=1)


def configurar_ejes(fig, escala_temporal, fecha_min, fecha_max):
    """Configurar los ejes X e Y con estilos modernos"""
    
    # Configuración del eje X según escala temporal
    if escala_temporal == "Días":
        fig.update_xaxes(
            dtick=86400000.0,  # Cada día
            tickformat="%d/%m",
            tickangle=45,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(225, 232, 237, 0.8)',
            title="📅 Días",
            title_font=dict(size=14, color='#2C3E50', family="Segoe UI"),
            tickfont=dict(size=10, color='#657786')
        )
    elif escala_temporal == "Semanas":
        fig.update_xaxes(
            dtick=86400000.0 * 7,  # Cada semana
            tickformat="Sem %U",
            tickangle=45,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(225, 232, 237, 0.8)',
            title="📅 Semanas",
            title_font=dict(size=14, color='#2C3E50', family="Segoe UI"),
            tickfont=dict(size=10, color='#657786')
        )
    elif escala_temporal == "Años":
        fig.update_xaxes(
            dtick="M12",  # Cada año
            tickformat="%Y",
            tickangle=0,
            showgrid=True,
            gridwidth=2,
            gridcolor='rgba(225, 232, 237, 0.8)',
            title="📅 Años",
            title_font=dict(size=14, color='#2C3E50', family="Segoe UI"),
            tickfont=dict(size=12, color='#657786')
        )
    else:  # Meses (por defecto)
        fig.update_xaxes(
            dtick="M1",
            tickformat="%b<br>%Y",
            tickangle=0,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(225, 232, 237, 0.8)',
            title="📅 Cronograma Mensual",
            title_font=dict(size=14, color='#2C3E50', family="Segoe UI"),
            tickfont=dict(size=10, color='#657786'),
            showspikes=True,
            spikecolor="rgba(68, 68, 68, 0.5)",
            spikesnap="cursor",
            spikemode="across"
        )
    
    # Configuración del eje Y
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(225, 232, 237, 0.5)',
        tickfont=dict(size=10, color='#14171A', family="Segoe UI"),
        title="📋 Tareas del Proyecto",
        title_font=dict(size=14, color='#2C3E50', family="Segoe UI"),
        categoryorder='total ascending',
        ticksuffix="  ",
        automargin=True
    )


def agregar_linea_hoy(fig, fecha_min, fecha_max):
    """Agregar línea indicadora del día actual"""
    hoy = datetime.now()
    if fecha_min <= hoy <= fecha_max:
        fig.add_shape(
            type="line",
            x0=hoy,
            x1=hoy,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(
                color="#E1306C",
                width=3
            ),
            opacity=0.9
        )
        
        # Agregar anotación
        fig.add_annotation(
            x=hoy,
            y=1.02,
            yref="paper",
            text="📍 HOY",
            showarrow=False,
            font=dict(
                size=12, 
                color="#E1306C", 
                family="Segoe UI"
            ),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E1306C",
            borderwidth=1
        )


def agregar_indicadores_mensuales(fig, fecha_min, fecha_max):
    """Agregar indicadores visuales para los meses"""
    meses_es = {
        1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
        7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
    }
    
    current_date = fecha_min.replace(day=1)
    while current_date <= fecha_max:
        # Agregar etiqueta del mes en la parte superior
        fig.add_annotation(
            x=current_date + timedelta(days=15),  # Centrado en el mes
            y=1.02,  # Arriba del gráfico
            text=f"<b>{meses_es[current_date.month]}</b>",
            showarrow=False,
            yref="paper",
            font=dict(size=11, color="#657786", family="Segoe UI"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#E1E8ED",
            borderwidth=1
        )
        
        # Siguiente mes
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

# Cargar datos
data = cargar_datos()

if data:
    # Procesar datos
    df = procesar_datos_gantt(data)
    
    # Sidebar con filtros
    st.sidebar.header("🔍 Filtros")
    
    # Selector de escala temporal
    st.sidebar.subheader("📅 Escala Temporal")
    escala_temporal = st.sidebar.selectbox(
        "Selecciona la escala de tiempo:",
        ["Días", "Semanas", "Meses", "Años"],
        index=2  # Por defecto "Meses"
    )
    
    # Filtro por carpeta
    carpetas = ["Todas"] + sorted(df['Carpeta'].unique().tolist())
    carpeta_seleccionada = st.sidebar.selectbox("📁 Carpeta:", carpetas)
    
    # Filtro por estado
    estados = ["Todos"] + sorted(df['Estado'].unique().tolist())
    estado_seleccionado = st.sidebar.multiselect("📊 Estado:", estados, default=["Todos"])
    
    # Filtro por prioridad
    prioridades = ["Todas"] + sorted(df['Prioridad'].unique().tolist())
    prioridad_seleccionada = st.sidebar.multiselect("⚡ Prioridad:", prioridades, default=["Todas"])
    
    # Filtro por asignado
    todos_asignados = set()
    for asignados in df['Asignados']:
        if asignados != "Sin asignar":
            todos_asignados.update([a.strip() for a in asignados.split(",")])
    
    asignados_list = ["Todos"] + sorted(list(todos_asignados))
    asignado_seleccionado = st.sidebar.selectbox("👤 Asignado:", asignados_list)
    
    # Filtro por rango de fechas
    st.sidebar.subheader("📅 Rango de Fechas")
    fecha_min = df['Fecha_Inicio'].min()
    fecha_max = df['Fecha_Limite'].max()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        fecha_inicio_filtro = st.date_input("Desde:", fecha_min)
    with col2:
        fecha_fin_filtro = st.date_input("Hasta:", fecha_max)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if carpeta_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Carpeta'] == carpeta_seleccionada]
    
    if "Todos" not in estado_seleccionado and estado_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['Estado'].isin(estado_seleccionado)]
    
    if "Todas" not in prioridad_seleccionada and prioridad_seleccionada:
        df_filtrado = df_filtrado[df_filtrado['Prioridad'].isin(prioridad_seleccionada)]
    
    if asignado_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Asignados'].str.contains(asignado_seleccionado, na=False)]
    
    # Filtro por fechas
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha_Inicio'].dt.date >= fecha_inicio_filtro) &
        (df_filtrado['Fecha_Limite'].dt.date <= fecha_fin_filtro)
    ]
    
    # Mostrar métricas con diseño moderno
    st.markdown("### 📊 Resumen del Proyecto")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcular métricas
    total_tareas = len(df_filtrado)
    pendientes = len(df_filtrado[df_filtrado['Estado'] == 'Pendiente'])
    en_progreso = len(df_filtrado[df_filtrado['Estado'] == 'En Progreso'])
    completadas = len(df_filtrado[df_filtrado['Estado'] == 'Completado'])
    
    # Calcular porcentaje de progreso
    progreso_pct = (completadas / total_tareas * 100) if total_tareas > 0 else 0
    
    with col1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{total_tareas}</div>
                <div style="font-size: 14px; opacity: 0.9;">📋 Total Tareas</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{pendientes}</div>
                <div style="font-size: 14px; opacity: 0.9;">⏳ Pendientes</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{en_progreso}</div>
                <div style="font-size: 14px; opacity: 0.9;">🔄 En Progreso</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #45B7D1 0%, #96CEB4 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">{completadas}</div>
                <div style="font-size: 14px; opacity: 0.9;">✅ Completadas</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">({progreso_pct:.1f}%)</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Mostrar información de la escala temporal con estilo moderno
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 15px 25px;
            border-radius: 12px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div style="color: white; font-size: 16px; font-weight: 600; margin-bottom: 5px;">
                📅 Escala Temporal Activa: {escala_temporal}
            </div>
            <div style="color: rgba(255,255,255,0.9); font-size: 14px;">
                El cronograma muestra la línea de tiempo organizada por <strong>{escala_temporal.lower()}</strong>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Encabezado visual moderno para la escala de meses
    if not df_filtrado.empty and escala_temporal == "Meses":
        fecha_inicio = df_filtrado['Fecha_Inicio'].min()
        fecha_fin = df_filtrado['Fecha_Limite'].max()
        
        # Crear información de meses
        meses_info = []
        current_date = fecha_inicio.replace(day=1)
        
        while current_date <= fecha_fin:
            meses_info.append({
                'mes': current_date.strftime('%B'),
                'mes_corto': current_date.strftime('%b'),
                'año': current_date.year,
                'numero': current_date.month
            })
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Mostrar encabezado visual moderno de meses
        if len(meses_info) <= 12:  # Solo mostrar si no son demasiados meses
            st.markdown("### 📅 Vista Mensual del Cronograma")
            
            # Crear columnas dinámicamente
            num_cols = min(len(meses_info), 6)  # Máximo 6 columnas
            filas_necesarias = (len(meses_info) + num_cols - 1) // num_cols
            
            for fila in range(filas_necesarias):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    mes_idx = fila * num_cols + col_idx
                    if mes_idx < len(meses_info):
                        mes_info = meses_info[mes_idx]
                        
                        # Colores diferentes para cada mes
                        colores_meses = [
                            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3",
                            "#54A0FF", "#5F27CD", "#00D2D3", "#FF9F43", "#10AC84", "#EE5A24"
                        ]
                        color = colores_meses[mes_info['numero'] - 1]
                        
                        with cols[col_idx]:
                            st.markdown(
                                f"""
                                <div style="
                                    background: {color};
                                    color: white;
                                    padding: 12px;
                                    border-radius: 8px;
                                    text-align: center;
                                    margin: 5px 0;
                                    font-weight: 600;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                                    transition: all 0.3s ease;
                                ">
                                    <div style="font-size: 14px;">{mes_info['mes_corto']}</div>
                                    <div style="font-size: 12px; opacity: 0.9;">{mes_info['año']}</div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
    
    # Crear y mostrar el diagrama de Gantt
    fig = crear_diagrama_gantt(df_filtrado, escala_temporal)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla de datos
    st.subheader("📋 Detalle de Tareas")
    
    # Formatear DataFrame para mostrar
    df_mostrar = df_filtrado[['Nombre_Completo', 'Carpeta', 'Lista', 'Estado', 'Asignados', 'Prioridad', 'Fecha_Inicio', 'Fecha_Limite']].copy()
    df_mostrar['Fecha_Inicio'] = df_mostrar['Fecha_Inicio'].dt.strftime('%d/%m/%Y')
    df_mostrar['Fecha_Limite'] = df_mostrar['Fecha_Limite'].dt.strftime('%d/%m/%Y')
    
    df_mostrar.columns = ['Tarea', 'Carpeta', 'Lista', 'Estado', 'Asignados', 'Prioridad', 'Fecha Inicio', 'Fecha Límite']
    
    st.dataframe(
        df_mostrar,
        use_container_width=True,
        hide_index=True
    )
    
    # Opción para descargar datos filtrados
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df_mostrar.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"tareas_filtradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        excel_data = exportar_a_excel(df_filtrado)
        if excel_data:
            st.download_button(
                label="📊 Descargar Excel",
                data=excel_data,
                file_name=f"tareas_gantt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Mostrar estadísticas avanzadas si está activado
    if st.session_state.get('show_stats', False):
        st.markdown("---")
        st.subheader("📈 Estadísticas Avanzadas del Proyecto")
        
        stats = calcular_estadisticas_avanzadas(df_filtrado)
        
        # Métricas de progreso
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📊 Progreso General", 
                f"{stats['progreso_porcentaje']:.1f}%",
                delta=f"{stats['progreso_porcentaje']:.1f}%" if stats['progreso_porcentaje'] > 50 else None
            )
        
        with col2:
            duracion_promedio = np.mean(list(stats['duracion_promedio'].values()))
            st.metric("⏱️ Duración Promedio", f"{duracion_promedio:.1f} días")
        
        with col3:
            personas_activas = len(stats['carga_trabajo'])
            st.metric("👥 Personas Activas", personas_activas)
        
        # Gráficos de estadísticas
        col1, col2 = st.columns(2)
        
        with col1:
            if stats['carga_trabajo']:
                st.subheader("👤 Carga de Trabajo por Persona")
                fig_carga = px.bar(
                    x=list(stats['carga_trabajo'].values()),
                    y=list(stats['carga_trabajo'].keys()),
                    orientation='h',
                    title="Número de Tareas Asignadas",
                    labels={'x': 'Número de Tareas', 'y': 'Persona'},
                    color=list(stats['carga_trabajo'].values()),
                    color_continuous_scale="viridis"
                )
                fig_carga.update_layout(height=400)
                st.plotly_chart(fig_carga, use_container_width=True)
        
        with col2:
            if stats['duracion_promedio']:
                st.subheader("⏱️ Duración Promedio por Estado")
                estados = list(stats['duracion_promedio'].keys())
                duraciones = list(stats['duracion_promedio'].values())
                
                fig_duracion = px.bar(
                    x=estados,
                    y=duraciones,
                    title="Días Promedio por Estado",
                    labels={'x': 'Estado', 'y': 'Días Promedio'},
                    color=duraciones,
                    color_continuous_scale="blues"
                )
                fig_duracion.update_layout(height=400)
                st.plotly_chart(fig_duracion, use_container_width=True)
    
    # Mostrar estadísticas adicionales
    with st.expander("📊 Estadísticas Adicionales"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Distribución por Estado")
            estado_counts = df_filtrado['Estado'].value_counts()
            fig_pie = px.pie(
                values=estado_counts.values,
                names=estado_counts.index,
                title="Distribución de Tareas por Estado",
                color_discrete_map={
                    "Pendiente": "#FF6B6B",
                    "En Progreso": "#4ECDC4", 
                    "Completado": "#45B7D1"
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("⚡ Distribución por Prioridad")
            prioridad_counts = df_filtrado['Prioridad'].value_counts()
            fig_bar = px.bar(
                x=prioridad_counts.index,
                y=prioridad_counts.values,
                title="Distribución de Tareas por Prioridad",
                labels={'x': 'Prioridad', 'y': 'Cantidad de Tareas'},
                color=prioridad_counts.values,
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.error("No se pudieron cargar los datos. Asegúrate de que el archivo 'tareas_sin_subtareas.json' esté presente.")
    st.info("💡 **Sugerencia:** Ejecuta primero el script 'main.py' para generar los datos desde ClickUp.")
