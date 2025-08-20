#!/usr/bin/env python3
"""
Ejecutor de Pruebas de Carga con Selección Individual
Permite ejecutar pruebas específicas usando argumentos de línea de comandos
"""

import subprocess
import time
import json
import argparse
import sys
from datetime import datetime
import os

class EjecutorPruebasCarga:
    def __init__(self):
        self.resultados = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Definir comandos disponibles
        self.comandos_disponibles = {
            'get': {
                'nombre': 'GET Verify Number',
                'descripcion': 'Prueba GET para verificación de número',
                'comando': 'wrk -t32 -c50000 -d300s -s get_verify_number_enhanced.lua https://yasta.bancounion.com.bo/gateway/user/verify/number?username=65663503',
                'script_lua': 'get_verify_number_enhanced.lua'
            },
            'post': {
                'nombre': 'POST Pagos',
                'descripcion': 'Prueba POST para procesamiento de pagos',
                'comando': 'wrk -t32 -c50000 -d300s -s post_pagos_enhanced.lua https://ws.pagosbolivia.com.bo:8443/api/pagos/ProcessMessage',
                'script_lua': 'post_pagos_enhanced.lua'
            }
        }
    
    def mostrar_ayuda(self):
        """Mostrar información de ayuda"""
        print("="*70)
        print("🚀 EJECUTOR DE PRUEBAS DE CARGA")
        print("="*70)
        print("\nUso:")
        print("  python3 ejecutar_pruebas_carga.py [OPCIÓN]")
        print("\nOpciones disponibles:")
        print("  get     - Ejecutar solo la prueba GET (verify number)")
        print("  post    - Ejecutar solo la prueba POST (pagos)")
        print("  ambas   - Ejecutar ambas pruebas secuencialmente")
        print("  -h      - Mostrar esta ayuda")
        print("\nEjemplos:")
        print("  python3 ejecutar_pruebas_carga.py get")
        print("  python3 ejecutar_pruebas_carga.py post")
        print("  python3 ejecutar_pruebas_carga.py ambas")
        print("\nDetalles de las pruebas:")
        for clave, info in self.comandos_disponibles.items():
            print(f"\n  {clave.upper()}:")
            print(f"    Nombre: {info['nombre']}")
            print(f"    Descripción: {info['descripcion']}")
            print(f"    Script Lua: {info['script_lua']}")
        print("\nConfiguración: 32 threads, 50000 conexiones, 300 segundos")
        print("="*70)
    
    def verificar_archivos_lua(self):
        """Verificar que los archivos Lua existan"""
        archivos_faltantes = []
        for clave, info in self.comandos_disponibles.items():
            if not os.path.exists(info['script_lua']):
                archivos_faltantes.append(info['script_lua'])
        
        if archivos_faltantes:
            print("❌ ERROR: Faltan archivos Lua necesarios:")
            for archivo in archivos_faltantes:
                print(f"  - {archivo}")
            print("\nPor favor asegúrate de que todos los archivos estén presentes.")
            return False
        return True
    
    def ejecutar_comando_wrk(self, nombre_prueba, info_comando):
        """Ejecutar un comando wrk específico"""
        comando = info_comando['comando']
        
        print(f"\n{'='*60}")
        print(f"🔄 Iniciando: {info_comando['nombre']}")
        print(f"📝 Descripción: {info_comando['descripcion']}")
        print(f"⚙️  Comando: {comando}")
        print(f"{'='*60}")
        
        tiempo_inicio = time.time()
        
        try:
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=400  # 400 segundos timeout
            )
            
            tiempo_fin = time.time()
            
            self.resultados[nombre_prueba] = {
                'comando': comando,
                'stdout': resultado.stdout,
                'stderr': resultado.stderr,
                'return_code': resultado.returncode,
                'execution_time': tiempo_fin - tiempo_inicio,
                'timestamp': datetime.now().isoformat(),
                'nombre_prueba': info_comando['nombre'],
                'descripcion': info_comando['descripcion']
            }
            
            print(f"\n✅ {info_comando['nombre']} completada en {tiempo_fin - tiempo_inicio:.2f} segundos")
            print(f"📊 Código de retorno: {resultado.returncode}")
            
            if resultado.stdout:
                print(f"\n📈 Resultados:")
                # Mostrar solo las líneas más importantes
                lineas = resultado.stdout.split('\n')
                for linea in lineas:
                    if any(palabra in linea for palabra in ['Requests/sec:', 'Latency', 'requests in', 'Transfer/sec']):
                        print(f"  {linea}")
                        
            if resultado.stderr:
                print(f"\n⚠️  Advertencias/Errores:\n{resultado.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ ERROR: {info_comando['nombre']} excedió el tiempo límite de 400 segundos")
            self.resultados[nombre_prueba] = {
                'comando': comando,
                'error': 'Timeout después de 400 segundos',
                'timestamp': datetime.now().isoformat(),
                'nombre_prueba': info_comando['nombre']
            }
        except Exception as e:
            print(f"❌ ERROR ejecutando {info_comando['nombre']}: {str(e)}")
            self.resultados[nombre_prueba] = {
                'comando': comando,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'nombre_prueba': info_comando['nombre']
            }
    
    def guardar_resultados(self):
        """Guardar resultados en archivo JSON"""
        nombre_archivo = f"resultados_pruebas_carga_{self.timestamp}.json"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados guardados en: {nombre_archivo}")
        return nombre_archivo
    
    def ejecutar_prueba_individual(self, tipo_prueba):
        """Ejecutar una prueba individual"""
        if tipo_prueba not in self.comandos_disponibles:
            print(f"❌ ERROR: Tipo de prueba '{tipo_prueba}' no válido.")
            print(f"Tipos disponibles: {', '.join(self.comandos_disponibles.keys())}")
            return False
        
        if not self.verificar_archivos_lua():
            return False
        
        print(f"🚀 Iniciando prueba individual: {tipo_prueba.upper()}")
        print(f"⏰ Timestamp: {self.timestamp}")
        
        info_comando = self.comandos_disponibles[tipo_prueba]
        nombre_prueba = f"{tipo_prueba}_test"
        
        self.ejecutar_comando_wrk(nombre_prueba, info_comando)
        
        # Guardar resultados
        archivo_resultados = self.guardar_resultados()
        
        print(f"\n{'='*60}")
        print("✅ PRUEBA INDIVIDUAL COMPLETADA")
        print(f"📁 Archivo de resultados: {archivo_resultados}")
        print(f"{'='*60}")
        
        return archivo_resultados
    
    def ejecutar_ambas_pruebas(self):
        """Ejecutar ambas pruebas secuencialmente"""
        if not self.verificar_archivos_lua():
            return False
        
        print("🚀 Iniciando ejecución de AMBAS pruebas")
        print(f"⏰ Timestamp: {self.timestamp}")
        
        # Ejecutar prueba GET
        print("\n🔄 FASE 1: Ejecutando prueba GET...")
        self.ejecutar_comando_wrk("GET_verify_number", self.comandos_disponibles['get'])
        
        # Esperar entre pruebas
        print("\n⏳ Esperando 10 segundos antes de la siguiente prueba...")
        time.sleep(10)
        
        # Ejecutar prueba POST
        print("\n🔄 FASE 2: Ejecutando prueba POST...")
        self.ejecutar_comando_wrk("POST_pagos", self.comandos_disponibles['post'])
        
        # Guardar resultados
        archivo_resultados = self.guardar_resultados()
        
        print(f"\n{'='*60}")
        print("✅ AMBAS PRUEBAS COMPLETADAS")
        print(f"📁 Archivo de resultados: {archivo_resultados}")
        print(f"{'='*60}")
        
        return archivo_resultados

def main():
    ejecutor = EjecutorPruebasCarga()
    
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Ejecutor de Pruebas de Carga con wrk',
        add_help=False  # Desactivar ayuda automática para usar la nuestra
    )
    parser.add_argument('tipo', nargs='?', 
                       choices=['get', 'post', 'ambas', 'help', '-h'], 
                       help='Tipo de prueba a ejecutar')
    
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        ejecutor.mostrar_ayuda()
        return
    
    try:
        args = parser.parse_args()
    except SystemExit:
        ejecutor.mostrar_ayuda()
        return
    
    # Mostrar ayuda si se solicita
    if args.tipo in ['help', '-h'] or args.tipo is None:
        ejecutor.mostrar_ayuda()
        return
    
    # Ejecutar según el tipo seleccionado
    if args.tipo == 'ambas':
        archivo_resultados = ejecutor.ejecutar_ambas_pruebas()
    else:
        archivo_resultados = ejecutor.ejecutar_prueba_individual(args.tipo)
    
    if archivo_resultados:
        print(f"\n🎯 SIGUIENTE PASO:")
        print(f"Para generar el reporte HTML ejecuta:")
        print(f"python3 generar_reporte_html.py")

if __name__ == "__main__":
    main()
