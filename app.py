#!/usr/bin/env python3
"""
🚀 Punto de entrada principal para Streamlit Cloud
Maneja errores de importación y configuración de manera robusta
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal que inicia la aplicación de manera segura"""
    try:
        # Importar y ejecutar la aplicación principal
        import gantt_app
        print("✅ Aplicación Gantt iniciada correctamente")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Verificando dependencias...")
        
        # Mostrar dependencias faltantes
        missing_deps = []
        try:
            import streamlit
        except ImportError:
            missing_deps.append("streamlit")
            
        try:
            import pandas
        except ImportError:
            missing_deps.append("pandas")
            
        try:
            import plotly
        except ImportError:
            missing_deps.append("plotly")
            
        if missing_deps:
            print(f"❌ Dependencias faltantes: {missing_deps}")
        
        raise
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("🔧 Iniciando en modo seguro...")
        
        # Intentar cargar una versión simplificada
        try:
            import streamlit as st
            st.title("🚨 Error en la Aplicación")
            st.error(f"Error: {str(e)}")
            st.info("La aplicación encontró un problema. Por favor, verifica la configuración.")
            
        except Exception as final_error:
            print(f"❌ Error crítico: {final_error}")
            sys.exit(1)

if __name__ == "__main__":
    main()
