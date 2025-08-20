#!/usr/bin/env python3
"""
Sistema Completo de Pruebas de Carga
Orquestador principal que ejecuta pruebas y genera reportes HTML automáticamente
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime

def verificar_dependencias():
    """Verificar e instalar dependencias necesarias"""
    paquetes_requeridos = ['matplotlib', 'seaborn', 'pandas', 'numpy', 'plotly', 'jinja2']
    paquetes_faltantes = []
    
    print("🔍 Verificando dependencias...")
    for paquete in paquetes_requeridos:
        try:
            __import__(paquete)
        except ImportError:
            paquetes_faltantes.append(paquete)
    
    if paquetes_faltantes:
        print(f"📦 Instalando dependencias faltantes: {', '.join(paquetes_faltantes)}")
        for paquete in paquetes_faltantes:
            subprocess.run([sys.executable, '-m', 'pip', 'install', paquete], check=True)
        print("✅ Dependencias instaladas exitosamente!")
    else:
        print("✅ Todas las dependencias están instaladas!")

def ejecutar_pruebas_y_generar_reporte(tipo_prueba):
    """Ejecutar pruebas y generar reporte HTML automáticamente"""
    print("="*80)
    print("🚀 SISTEMA COMPLETO DE PRUEBAS DE CARGA")
    print("="*80)
    print(f"Iniciado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tipo de prueba: {tipo_prueba.upper()}")
    print()
    
    # Verificar dependencias
    verificar_dependencias()
    
    # Paso 1: Ejecutar pruebas de carga
    print("\n" + "="*50)
    print("📊 PASO 1: Ejecutando pruebas de carga...")
    print("="*50)
    
    resultado = subprocess.run([sys.executable, 'ejecutar_pruebas_carga.py', tipo_prueba], 
                              capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print("❌ ERROR: Las pruebas de carga fallaron!")
        print("STDOUT:", resultado.stdout)
        print("STDERR:", resultado.stderr)
        return False
    
    print("✅ Pruebas de carga completadas exitosamente!")
    print(resultado.stdout)
    
    # Paso 2: Generar reporte HTML
    print("\n" + "="*50)
    print("🎨 PASO 2: Generando reporte HTML interactivo...")
    print("="*50)
    
    resultado = subprocess.run([sys.executable, 'generar_reporte_html.py'], 
                              capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print("❌ ERROR: La generación del reporte HTML falló!")
        print("STDOUT:", resultado.stdout)
        print("STDERR:", resultado.stderr)
        return False
    
    print("✅ Reporte HTML generado exitosamente!")
    print(resultado.stdout)
    
    # Mostrar archivos generados
    print("\n" + "="*80)
    print("🎉 SISTEMA COMPLETADO EXITOSAMENTE!")
    print("="*80)
    
    print("\n📁 Archivos generados:")
    archivos = os.listdir('.')
    archivos_generados = []
    
    for archivo in sorted(archivos):
        if (archivo.startswith('resultados_pruebas_carga_') or 
            archivo.startswith('dashboard_pruebas_carga_')):
            archivos_generados.append(archivo)
            tipo_archivo = "JSON" if archivo.endswith('.json') else "HTML"
            print(f"  📄 {archivo} ({tipo_archivo})")
    
    # Encontrar el archivo HTML más reciente
    archivos_html = [f for f in archivos_generados if f.endswith('.html')]
    if archivos_html:
        archivo_html_reciente = sorted(archivos_html)[-1]
        print(f"\n🌐 Para ver el dashboard interactivo, abre en tu navegador:")
        print(f"   {os.path.abspath(archivo_html_reciente)}")
    
    return True

def mostrar_ayuda():
    """Mostrar información de ayuda del sistema completo"""
    print("="*80)
    print("🚀 SISTEMA COMPLETO DE PRUEBAS DE CARGA")
    print("="*80)
    print("\nEste script ejecuta automáticamente:")
    print("  1. Las pruebas de carga con wrk")
    print("  2. La generación del reporte HTML interactivo")
    print("\nUso:")
    print("  python3 sistema_completo_pruebas.py [TIPO_PRUEBA]")
    print("\nTipos de prueba disponibles:")
    print("  get     - Solo prueba GET (verify number)")
    print("  post    - Solo prueba POST (pagos)")
    print("  ambas   - Ambas pruebas secuencialmente")
    print("\nEjemplos:")
    print("  python3 sistema_completo_pruebas.py get")
    print("  python3 sistema_completo_pruebas.py post")
    print("  python3 sistema_completo_pruebas.py ambas")
    print("\nEl sistema generará:")
    print("  📊 Archivo JSON con resultados detallados")
    print("  🌐 Dashboard HTML interactivo con gráficos")
    print("\nComandos originales incluidos:")
    print("  GET:  wrk -t12 -c3000 -d300s -s get_verify_number.lua")
    print("  POST: wrk -t12 -c3000 -d300s -s post_pagos.lua")
    print("="*80)

def main():
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Sistema Completo de Pruebas de Carga',
        add_help=False
    )
    parser.add_argument('tipo', nargs='?', 
                       choices=['get', 'post', 'ambas', 'help', '-h'], 
                       help='Tipo de prueba a ejecutar')
    
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        mostrar_ayuda()
        return
    
    try:
        args = parser.parse_args()
    except SystemExit:
        mostrar_ayuda()
        return
    
    # Mostrar ayuda si se solicita
    if args.tipo in ['help', '-h'] or args.tipo is None:
        mostrar_ayuda()
        return
    
    # Ejecutar sistema completo
    exito = ejecutar_pruebas_y_generar_reporte(args.tipo)
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
