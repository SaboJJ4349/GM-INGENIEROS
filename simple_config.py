"""
🔐 Configuración Simple y Robusta para Streamlit Cloud
Sin dependencias complejas que puedan fallar en el inicio
"""

import os

def get_simple_config():
    """
    Obtiene configuración de manera muy simple y robusta
    """
    config = {
        'api_token': None,
        'space_id': '90111892233',
        'environment': 'demo',
        'debug_mode': True
    }
    
    # Intentar obtener de variables de entorno primero
    api_token = os.getenv('CLICKUP_API_TOKEN')
    space_id = os.getenv('CLICKUP_SPACE_ID')
    
    if api_token:
        config['api_token'] = api_token
        config['environment'] = 'production'
        config['debug_mode'] = False
        
    if space_id:
        config['space_id'] = space_id
    
    # Intentar Streamlit secrets solo si está disponible
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets and 'clickup' in st.secrets:
            config['api_token'] = st.secrets.clickup.api_token
            config['space_id'] = st.secrets.clickup.space_id
            config['environment'] = 'production'
            config['debug_mode'] = False
    except:
        # Si hay cualquier error con secrets, usar configuración por defecto
        pass
    
    return config

def is_demo_mode(config):
    """Verifica si está en modo demo"""
    return config.get('environment') == 'demo' or not config.get('api_token')

def get_masked_token(token):
    """Enmascara token para logs seguros"""
    if not token:
        return "No configurado"
    if len(token) > 10:
        return f"{token[:6]}...{token[-4:]}"
    return "***"
