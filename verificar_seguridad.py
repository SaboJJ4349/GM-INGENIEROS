#!/usr/bin/env python3
"""
🔐 Script de Verificación de Seguridad
Verifica que la aplicación esté configurada de manera segura antes del despliegue
"""

import os
import re
import glob
import sys

def verificar_tokens_en_codigo():
    """Verifica que no hay tokens hardcodeados en el código"""
    print("🔍 Verificando tokens en código fuente...")
    
    archivos_python = glob.glob("*.py")
    tokens_encontrados = []
    
    patron_token = re.compile(r'pk_[A-Za-z0-9_]+')
    
    for archivo in archivos_python:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            matches = patron_token.findall(contenido)
            if matches:
                tokens_encontrados.append((archivo, matches))
    
    if tokens_encontrados:
        print("❌ TOKENS ENCONTRADOS EN CÓDIGO:")
        for archivo, tokens in tokens_encontrados:
            print(f"   📄 {archivo}: {tokens}")
        return False
    else:
        print("✅ No se encontraron tokens hardcodeados")
        return True

def verificar_gitignore():
    """Verifica que .gitignore protege archivos sensibles"""
    print("🔍 Verificando .gitignore...")
    
    if not os.path.exists('.gitignore'):
        print("❌ Archivo .gitignore no encontrado")
        return False
    
    with open('.gitignore', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    archivos_criticos = [
        'secrets.toml',
        '.env',
        '*.env'
    ]
    
    missing = []
    for archivo in archivos_criticos:
        if archivo not in contenido:
            missing.append(archivo)
    
    if missing:
        print(f"❌ Archivos faltantes en .gitignore: {missing}")
        return False
    else:
        print("✅ .gitignore protege archivos sensibles")
        return True

def verificar_secrets_locales():
    """Verifica configuración de secrets locales"""
    print("🔍 Verificando secrets locales...")
    
    secrets_path = '.streamlit/secrets.toml'
    
    if os.path.exists(secrets_path):
        print("✅ Archivo secrets.toml encontrado")
        
        # Verificar que tiene la estructura correcta
        with open(secrets_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if '[clickup]' in contenido and 'api_token' in contenido:
            print("✅ Estructura de secrets correcta")
            return True
        else:
            print("❌ Estructura de secrets incorrecta")
            return False
    else:
        print("⚠️  Archivo secrets.toml no encontrado (normal para producción)")
        return True

def verificar_variables_entorno():
    """Verifica variables de entorno"""
    print("🔍 Verificando variables de entorno...")
    
    token = os.getenv('CLICKUP_API_TOKEN')
    space_id = os.getenv('CLICKUP_SPACE_ID')
    
    if token:
        print("✅ CLICKUP_API_TOKEN configurado")
        if token.startswith('pk_'):
            print("✅ Formato de token correcto")
        else:
            print("❌ Formato de token incorrecto")
            return False
    else:
        print("⚠️  CLICKUP_API_TOKEN no configurado (puede usar secrets)")
    
    if space_id:
        print("✅ CLICKUP_SPACE_ID configurado")
    else:
        print("⚠️  CLICKUP_SPACE_ID no configurado")
    
    return True

def verificar_dependencias():
    """Verifica que requirements.txt está actualizado"""
    print("🔍 Verificando dependencias...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt no encontrado")
        return False
    
    dependencias_requeridas = [
        'streamlit',
        'pandas',
        'plotly',
        'requests',
        'openpyxl'
    ]
    
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        contenido = f.read().lower()
    
    missing = []
    for dep in dependencias_requeridas:
        if dep not in contenido:
            missing.append(dep)
    
    if missing:
        print(f"❌ Dependencias faltantes: {missing}")
        return False
    else:
        print("✅ Todas las dependencias están presentes")
        return True

def main():
    """Función principal de verificación"""
    print("🔐 VERIFICACIÓN DE SEGURIDAD - ClickUp Gantt App")
    print("=" * 50)
    
    verificaciones = [
        verificar_tokens_en_codigo,
        verificar_gitignore,
        verificar_secrets_locales,
        verificar_variables_entorno,
        verificar_dependencias
    ]
    
    resultados = []
    for verificacion in verificaciones:
        resultado = verificacion()
        resultados.append(resultado)
        print()
    
    # Resumen
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 30)
    
    exitosos = sum(resultados)
    total = len(resultados)
    
    if exitosos == total:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ Tu aplicación está lista para despliegue seguro")
        sys.exit(0)
    else:
        print(f"⚠️  {exitosos}/{total} verificaciones pasaron")
        print("❌ Revisa los errores antes de desplegar")
        sys.exit(1)

if __name__ == "__main__":
    main()
