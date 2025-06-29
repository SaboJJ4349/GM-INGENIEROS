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
    return {
        'environment': 'local',
        'data_source': 'json_file',
        'app_ready': True
    }

def cargar_datos():
    archivo = "tareas_sin_subtareas.json"
    if os.path.exists(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f), "real"
        except Exception as e:
            st.warning(f"Error al cargar JSON: {e}")
    ejemplo = {
        "Administración y Sistemas": {
            "SistemasGM": {
                "Tareas": {
                    "pendiente": [{
                        "nombre": "Implementar Sistema de Facturación",
                        "estado": "pendiente",
                        "asignados": ["Juan Pérez"],
                        "fecha_inicio": "01/07/25",
                        "fecha_limite": "15/07/25",
                        "prioridad": "high"
                    }],
                    "en progreso": [{
                        "nombre": "Desarrollo API REST",
                        "estado": "en progreso",
                        "asignados": ["Carlos López"],
                        "fecha_inicio": "15/06/25",
                        "fecha_limite": "30/06/25",
                        "prioridad": "urgent"
                    }],
                    "completado": [{
                        "nombre": "Análisis de Requerimientos",
                        "estado": "completado",
                        "asignados": ["Pedro Sánchez"],
                        "fecha_inicio": "01/06/25",
                        "fecha_limite": "15/06/25",
                        "prioridad": "normal"
                    }]
                }
            }
        }
    }
    return ejemplo, "ejemplo"

def procesar_datos_para_tabla(datos):
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
    if not fecha_str or fecha_str == 'N/A':
        return None
    try:
        if '/' in fecha_str:
            return datetime.strptime(fecha_str, '%d/%m/%y')
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except:
        return None

def crear_diagrama_gantt(df):
    if df.empty:
        return None
    gantt_data = []
    color_map = {'completado':'#28a745','en progreso':'#ffc107','pendiente':'#dc3545'}
    for _, row in df.iterrows():
        inicio = convertir_fecha(row['Fecha Inicio']) or datetime.now()
        fin = convertir_fecha(row['Fecha Límite']) or (inicio + timedelta(days=7))
        gantt_data.append({
            'Task': row['Tarea'][:50] + ('...' if len(row['Tarea'])>50 else ''),
            'Start': inicio,
            'Finish': fin,
            'Resource': row['Área'],
            'Estado': row['Estado'],
            'Asignados': row['Asignados'],
            'Prioridad': row['Prioridad'],
            'Color': color_map.get(row['Estado'], '#6c757d')
        })
    fig = go.Figure()
    for i, t in enumerate(gantt_data):
        fig.add_trace(go.Scatter(
            x=[t['Start'], t['Finish']],
            y=[i, i],
            mode='lines',
            line=dict(color=t['Color'], width=20),
            text=f"<b>{t['Task']}</b><br>Estado: {t['Estado']}<br>Asignados: {t['Asignados']}<br>Prioridad: {t['Prioridad']}",
            hovertemplate='%{text}<extra></extra>',
            showlegend=False
        ))
    fig.update_layout(
        title="📅 Diagrama de Gantt - Cronograma de Tareas",
        xaxis_title="Fecha",
        yaxis_title="Tareas",
        height=max(400, len(gantt_data)*40+100),
        yaxis=dict(tickmode='array', tickvals=list(range(len(gantt_data))),
                   ticktext=[d['Task'] for d in gantt_data], showgrid=True),
        xaxis=dict(type='date', showgrid=True),
        hovermode='closest', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def crear_cronograma_simple(df):
    if df.empty:
        return None
    fechas = []
    for _, row in df.iterrows():
        f = convertir_fecha(row['Fecha Límite'])
        if f:
            fechas.append({'Fecha': f.strftime('%Y-%m-%d'), 'Estado': row['Estado'], 'Tarea': row['Tarea']})
    if not fechas:
        return None
    df_f = pd.DataFrame(fechas)
    cron = df_f.groupby(['Fecha','Estado']).size().reset_index(name='Cantidad')
    fig = px.bar(cron, x='Fecha', y='Cantidad', color='Estado',
                 title="📆 Cronograma de Entregas por Estado",
                 color_discrete_map={'completado':'#28a745','en progreso':'#ffc107','pendiente':'#dc3545'})
    fig.update_layout(height=400)
    return fig

def aplicar_filtros(df, filtros):
    df_f = df.copy()
    if filtros['estados']:
        df_f = df_f[df_f['Estado'].isin(filtros['estados'])]
    if filtros['prioridades']:
        df_f = df_f[df_f['Prioridad'].isin(filtros['prioridades'])]
    if filtros.get('carpetas'):
        df_f = df_f[df_f['Carpeta'].isin(filtros['carpetas'])]
    if filtros.get('asignados'):
        def fa(s): return any(a in filtros['asignados'] for a in (s.split(',') if s and s!='N/A' else []))
        df_f = df_f[df_f['Asignados'].apply(fa)]
    if filtros.get('fecha_inicio') and filtros.get('fecha_fin'):
        def inrange(fs):
            f = convertir_fecha(fs)
            if not f:
                return False
            return filtros['fecha_inicio'] <= f.date() <= filtros['fecha_fin']
        df_f = df_f[df_f['Fecha Límite'].apply(inrange)]
    if filtros['buscar_texto']:
        df_f = df_f[df_f['Tarea'].str.contains(filtros['buscar_texto'], case=False, na=False)]
    fr = filtros['filtro_rapido']; hoy = datetime.now().date()
    if fr == "Solo Pendientes": df_f = df_f[df_f['Estado']=="pendiente"]
    elif fr == "Solo En Progreso": df_f = df_f[df_f['Estado']=="en progreso"]
    elif fr == "Solo Completadas": df_f = df_f[df_f['Estado']=="completado"]
    elif fr == "Prioridad Alta": df_f = df_f[df_f['Prioridad'].isin(['high','urgent'])]
    elif fr == "Sin Asignar": df_f = df_f[df_f['Asignados'].isin(['','N/A'])]
    elif fr == "Vencidas Pendientes":
        df_f = df_f[(df_f['Estado']!="completado") & (df_f['Fecha Límite'].apply(lambda f: convertir_fecha(f) and convertir_fecha(f).date() < hoy))]
    elif fr == "Esta Semana":
        inicio = hoy - timedelta(days=hoy.weekday()); fin = inicio + timedelta(days=6)
        df_f = df_f[df_f['Fecha Límite'].apply(lambda f: convertir_fecha(f) and inicio <= convertir_fecha(f).date() <= fin)]
    elif fr == "Próximos 7 Días":
        df_f = df_f[df_f['Fecha Límite'].apply(lambda f: convertir_fecha(f) and hoy <= convertir_fecha(f).date() <= hoy + timedelta(days=7))]
    if filtros['solo_activas']: df_f = df_f[df_f['Estado'] != 'completado']
    return df_f

# ===== APLICACIÓN PRINCIPAL =====
def main():
    st.title("📊 Dashboard de Gestión de Tareas ClickUp")
    datos, tipo = cargar_datos(); df = procesar_datos_para_tabla(datos)
    if df.empty: st.error("❌ No hay datos para mostrar"); return
    with st.sidebar:
        st.markdown("###  Filtros")
        est = st.multiselect("📊 Estado", options=df['Estado'].unique(), default=df['Estado'].unique(), key="filtro_estados")
        pr = st.multiselect("🎯 Prioridad", options=df['Prioridad'].unique(), default=df['Prioridad'].unique(), key="filtro_prioridades")
        crp = st.multiselect("📁 Carpeta", options=df['Carpeta'].unique(), default=df['Carpeta'].unique(), key="filtro_carpetas")
        todos = set(a for s in df['Asignados'] if s and s!='N/A' for a in s.split(','))
        asi = st.multiselect("👥 Asignados", options=sorted(todos), default=sorted(todos), key="filtro_asignados")
        fechas = [convertir_fecha(f).date() for f in df['Fecha Límite'] if convertir_fecha(f)]
        uso = st.checkbox("Activar filtro de fechas", key="usar_filtro_fechas")
        if fechas and uso:
            fi = st.date_input("Desde", min_value=min(fechas), max_value=max(fechas), value=min(fechas), key="fecha_inicio")
            ff = st.date_input("Hasta", min_value=min(fechas), max_value=max(fechas), value=max(fechas), key="fecha_fin")
        else: fi = ff = None
        fr = st.selectbox("⚡ Filtro Rápido", options=["Todos","Solo Pendientes","Solo En Progreso","Solo Completadas","Prioridad Alta","Sin Asignar","Vencidas Pendientes","Esta Semana","Pr óximos 7 Días"], key="filtro_rapido")
        tx = st.text_input("🔍 Buscar", placeholder="Nombre de tarea...", key="buscar_texto")
        sa = st.checkbox("Solo activas", help="Ocultar completadas", key="solo_activas")
        if st.button("🔄 Limpiar", key="limpiar"): st.rerun()
    filtros = {'estados': est, 'prioridades': pr, 'carpetas': crp, 'asignados': asi, 'fecha_inicio': fi if uso else None, 'fecha_fin': ff if uso else None, 'filtro_rapido': fr, 'buscar_texto': tx, 'solo_activas': sa}
    df_f = aplicar_filtros(df, filtros)
    if tipo == "ejemplo": st.info("📄 Usando datos de ejemplo. Coloca 'tareas_sin_subtareas.json' para datos reales.")
    else: st.success("📄 Datos cargados desde JSON local")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total", len(df_f)); c2.metric("⏳ Pendientes", len(df_f[df_f['Estado']=="pendiente"]))
    c3.metric("🔄 En Progreso", len(df_f[df_f['Estado']=="en progreso"]))
    c4.metric("✅ Completadas", len(df_f[df_f['Estado']=="completado"]))
    if len(df_f) < len(df): st.info(f"📊 Mostrando {len(df_f)} de {len(df)} tareas")
    tab1, tab2, tab3, tab4 = st.tabs(["📅 DIAGRAMA DE GANTT","📊 Dashboard","📆 Cronograma","📋 Tabla"]);
    with tab1:
        st.subheader("📅 Diagrama de Gantt");
        if not df_f.empty:
            fig = crear_diagrama_gantt(df_f)
            if fig: st.plotly_chart(fig, use_container_width=True)
            else: st.warning("No se pudo generar el diagrama.")
        else: st.warning("Sin tareas para Gantt.")
    with tab2:
        st.subheader("📊 Dashboard");
        if not df_f.empty:
            ec = df_f['Estado'].value_counts();
            if not ec.empty:
                fig1 = px.pie(values=ec.values, names=ec.index, title="Distribución por Estado", color_discrete_map={'completado':'#28a745','en progreso':'#ffc107','pendiente':'#dc3545'}); fig1.update_layout(height=400); st.plotly_chart(fig1, use_container_width=True)
            pc = df_f['Prioridad'].value_counts();
            if not pc.empty:
                fig2 = px.bar(x=pc.index, y=pc.values, title="Distribución por Prioridad", color=pc.index, color_discrete_map={'urgent':'#dc3545','high':'#fd7e14','normal':'#ffc107','low':'#28a745'}); fig2.update_layout(height=400); st.plotly_chart(fig2, use_container_width=True)
        else: st.warning("No hay datos para mostrar.")
    with tab3:
        st.subheader("📆 Cronograma de Entregas");
        if not df_f.empty:
            fig3 = crear_cronograma_simple(df_f)
            if fig3: st.plotly_chart(fig3, use_container_width=True)
            else: st.warning("No se pudo generar el cronograma.")
        else: st.warning("Sin tareas para cronograma.")
    with tab4:
        st.subheader("📋 Tabla de Tareas");
        if not df_f.empty:
            st.dataframe(df_f, use_container_width=True, hide_index=True)
            csv = df_f.to_csv(index=False)
            st.download_button("📥 Descargar CSV", data=csv, file_name=f"tareas_clickup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
        else: st.warning("Sin datos en la tabla.")

if __name__ == "__main__":
    main()
