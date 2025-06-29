import streamlit as st
import os
import json

def get_config():
    """
    Obtiene la configuración de manera segura desde Streamlit secrets o variables de entorno
    """
    config = {}
    
    try:
        # En producción (Streamlit Cloud), usar st.secrets
        if hasattr(st, 'secrets') and st.secrets:
            if 'clickup' in st.secrets:
                config['api_token'] = st.secrets.clickup.api_token
                config['space_id'] = st.secrets.clickup.space_id
                
                # Manejar configuración de app de manera segura
                app_config = st.secrets.get('app', {})
                config['environment'] = app_config.get('environment', 'production') if app_config else 'production'
                config['debug_mode'] = app_config.get('debug_mode', False) if app_config else False
                
                return config
        
        # Fallback a variables de entorno
        if os.getenv('CLICKUP_API_TOKEN'):
            config['api_token'] = os.getenv('CLICKUP_API_TOKEN')
            config['space_id'] = os.getenv('CLICKUP_SPACE_ID', '90111892233')
            config['environment'] = os.getenv('APP_ENVIRONMENT', 'production')
            config['debug_mode'] = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
            return config
        
    except Exception as e:
        # Si hay error accediendo a secrets, continuar con modo demo
        pass
    
    # Modo demo con datos de ejemplo
    config['api_token'] = None
    config['space_id'] = None
    config['environment'] = 'demo'
    config['debug_mode'] = True
    
    return config

def validate_config(config):
    """
    Valida que la configuración sea correcta
    """
    if config['environment'] == 'demo':
        st.info("🧪 Ejecutando en modo DEMO con datos de ejemplo")
        return True
    
    if not config.get('api_token'):
        st.error("🚨 Error: No se encontró el token de API de ClickUp")
        st.info("💡 Configura el token en los secrets de Streamlit Cloud o como variable de entorno")
        st.info("🧪 La aplicación continuará en modo DEMO")
        # Cambiar a modo demo en lugar de fallar
        config['environment'] = 'demo'
        config['api_token'] = None
        config['space_id'] = None
        config['debug_mode'] = True
        return True
    
    if not config.get('space_id'):
        st.warning("⚠️ No se encontró el ID del espacio de ClickUp, usando valor por defecto")
        config['space_id'] = '90111892233'
    
    # Validar formato del token
    if config.get('api_token') and not config['api_token'].startswith('pk_'):
        st.error("🚨 Error: El token de API no tiene el formato correcto (debe empezar con 'pk_')")
        st.info("🧪 La aplicación continuará en modo DEMO")
        config['environment'] = 'demo'
        config['api_token'] = None
        config['space_id'] = None
        config['debug_mode'] = True
        return True
    
    return True

def get_safe_headers(api_token):
    """
    Genera headers seguros para las peticiones a la API
    """
    if not api_token:
        return None
    
    return {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }

def log_debug(message, config):
    """
    Función de logging para debug
    """
    if config.get('debug_mode', False):
        st.sidebar.write(f"🐛 DEBUG: {message}")

def mask_token(token):
    """
    Enmascara el token para logging seguro
    """
    if not token:
        return "No configurado"
    
    if len(token) > 10:
        return f"{token[:6]}...{token[-4:]}"
    return "***"

def show_config_status(config):
    """
    Muestra el estado de la configuración de manera segura
    """
    try:
        with st.sidebar:
            st.markdown("### 🔧 Estado de Configuración")
            
            # Ambiente
            if config.get('environment') == 'demo':
                st.info("🧪 Modo DEMO - Datos de ejemplo")
            elif config.get('environment') == 'development':
                st.warning("🛠️ Modo DESARROLLO")
            else:
                st.success("🚀 Modo PRODUCCIÓN")
            
            # Token status
            token_status = "✅ Configurado" if config.get('api_token') else "❌ No configurado"
            st.write(f"**API Token:** {token_status}")
            
            if config.get('debug_mode') and config.get('api_token'):
                st.write(f"**Token (masked):** {mask_token(config['api_token'])}")
            
            # Space ID status
            space_status = "✅ Configurado" if config.get('space_id') else "❌ No configurado"
            st.write(f"**Space ID:** {space_status}")
            
            if config.get('debug_mode') and config.get('space_id'):
                st.write(f"**Space ID:** {config['space_id']}")
    except Exception as e:
        # Si hay error mostrando el estado, continuar silenciosamente
        pass
