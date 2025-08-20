#!/usr/bin/env python3
"""
Generador de Reportes HTML para Pruebas de Carga
Crea dashboard interactivo con gráficos detallados usando Plotly
"""

import json
import re
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from jinja2 import Template

class AnalizadorHTML:
    def __init__(self, archivo_resultados=None):
        self.archivo_resultados = archivo_resultados
        self.datos_parseados = {}
        
    def parsear_salida_wrk(self, texto_salida):
        """Parsear la salida de wrk y extraer métricas"""
        datos = {}
        
        # Extraer métricas básicas
        requests_match = re.search(r'(\d+) requests in ([\d.]+)s', texto_salida)
        if requests_match:
            datos['total_requests'] = int(requests_match.group(1))
            datos['duracion'] = float(requests_match.group(2))
            datos['rps'] = datos['total_requests'] / datos['duracion']
        
        # Extraer requests por segundo
        rps_match = re.search(r'Requests/sec:\s+([\d.]+)', texto_salida)
        if rps_match:
            datos['rps_reportado'] = float(rps_match.group(1))
        
        # Extraer transferencia por segundo
        transfer_sec_match = re.search(r'Transfer/sec:\s+([\d.]+)MB', texto_salida)
        if transfer_sec_match:
            datos['transferencia_por_seg'] = float(transfer_sec_match.group(1))
        
        # Extraer estadísticas de latencia
        latency_section = re.search(r'Latency\s+([\d.]+\w+)\s+([\d.]+\w+)\s+([\d.]+\w+)\s+([\d.]+)%', texto_salida)
        if latency_section:
            datos['latencia_promedio'] = self.parsear_unidad_tiempo(latency_section.group(1))
            datos['latencia_stdev'] = self.parsear_unidad_tiempo(latency_section.group(2))
            datos['latencia_max'] = self.parsear_unidad_tiempo(latency_section.group(3))
        
        # Extraer datos de percentiles
        percentiles = {}
        perc_matches = re.findall(r'(\d+)%\s+([\d.]+\w+)', texto_salida)
        for perc, valor in perc_matches:
            percentiles[f'p{perc}'] = self.parsear_unidad_tiempo(valor)
        datos['percentiles'] = percentiles
        
        # Extraer información de errores
        errors_match = re.search(r'Socket errors: connect (\d+), read (\d+), write (\d+), timeout (\d+)', texto_salida)
        if errors_match:
            datos['errores'] = {
                'conexion': int(errors_match.group(1)),
                'lectura': int(errors_match.group(2)),
                'escritura': int(errors_match.group(3)),
                'timeout': int(errors_match.group(4))
            }
            datos['total_errores'] = sum(datos['errores'].values())
        else:
            datos['errores'] = {'conexion': 0, 'lectura': 0, 'escritura': 0, 'timeout': 0}
            datos['total_errores'] = 0
        
        # Calcular conexiones exitosas y fallidas
        total_requests = datos.get('total_requests', 0)
        total_errores_conexion = datos['errores']['conexion']
        datos['conexiones_exitosas'] = total_requests
        datos['conexiones_fallidas'] = total_errores_conexion
        datos['total_conexiones_intentadas'] = total_requests + total_errores_conexion
        
        # Extraer métricas mejoradas del script Lua
        if '=== GET VERIFY NUMBER RESULTS ===' in texto_salida or '=== POST PAGOS RESULTS ===' in texto_salida:
            datos.update(self.parsear_metricas_mejoradas(texto_salida))
        
        return datos
    
    def parsear_metricas_mejoradas(self, texto_salida):
        """Parsear métricas mejoradas del script Lua"""
        mejoradas = {}
        
        # Extraer distribución de códigos de estado
        status_section = re.search(r'Status Code Distribution:(.*?)(?=\n\n|\nLatency Stats|$)', texto_salida, re.DOTALL)
        if status_section:
            codigos_estado = {}
            for linea in status_section.group(1).strip().split('\n'):
                match = re.search(r'(\d+):\s+(\d+)\s+requests', linea.strip())
                if match:
                    codigos_estado[int(match.group(1))] = int(match.group(2))
            mejoradas['codigos_estado'] = codigos_estado
        
        return mejoradas
    
    def parsear_unidad_tiempo(self, tiempo_str):
        """Convertir string de tiempo a milisegundos"""
        if 'us' in tiempo_str:
            return float(tiempo_str.replace('us', '')) / 1000
        elif 'ms' in tiempo_str:
            return float(tiempo_str.replace('ms', ''))
        elif 's' in tiempo_str:
            return float(tiempo_str.replace('s', '')) * 1000
        else:
            return float(tiempo_str)
    
    def cargar_resultados(self, archivo_resultados):
        """Cargar resultados desde archivo JSON"""
        with open(archivo_resultados, 'r') as f:
            resultados_raw = json.load(f)
        
        for nombre_prueba, datos_prueba in resultados_raw.items():
            if 'stdout' in datos_prueba:
                self.datos_parseados[nombre_prueba] = self.parsear_salida_wrk(datos_prueba['stdout'])
                self.datos_parseados[nombre_prueba]['salida_raw'] = datos_prueba['stdout']
                self.datos_parseados[nombre_prueba]['tiempo_ejecucion'] = datos_prueba.get('execution_time', 0)
    
    def crear_graficos_interactivos(self):
        """Crear dashboard HTML interactivo con Plotly"""
        if not self.datos_parseados:
            return None
        
        if len(self.datos_parseados) >= 2:
            return self.crear_dashboard_comparacion()
        else:
            return self.crear_dashboard_prueba_unica()
    
    def crear_dashboard_comparacion(self):
        """Crear dashboard de comparación para dos pruebas"""
        nombres_pruebas = list(self.datos_parseados.keys())
        nombre_prueba1 = nombres_pruebas[0]
        nombre_prueba2 = nombres_pruebas[1]
        datos_prueba1 = self.datos_parseados[nombre_prueba1]
        datos_prueba2 = self.datos_parseados[nombre_prueba2]
        
        # Crear subplots
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=[
                'Requests por Segundo', 'Latencia Promedio', 'Conexiones Exitosas vs Fallidas',
                'Tasa de Errores', 'Percentiles de Latencia', 'Total de Requests',
                'Tipos de Errores', 'Distribución de Conexiones', 'Resumen de Rendimiento'
            ],
            specs=[
                [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "pie"}, {"type": "table"}]
            ]
        )
        
        # 1. RPS Comparación
        fig.add_trace(
            go.Bar(
                x=[nombre_prueba1.replace('_', ' '), nombre_prueba2.replace('_', ' ')],
                y=[datos_prueba1.get('rps_reportado', 0), datos_prueba2.get('rps_reportado', 0)],
                name='RPS',
                marker_color=['#FF6B6B', '#4ECDC4'],
                text=[f"{datos_prueba1.get('rps_reportado', 0):.1f}", f"{datos_prueba2.get('rps_reportado', 0):.1f}"],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # 2. Latencia Comparación
        fig.add_trace(
            go.Bar(
                x=[nombre_prueba1.replace('_', ' '), nombre_prueba2.replace('_', ' ')],
                y=[datos_prueba1.get('latencia_promedio', 0), datos_prueba2.get('latencia_promedio', 0)],
                name='Latencia',
                marker_color=['#FFE66D', '#FF6B6B'],
                text=[f"{datos_prueba1.get('latencia_promedio', 0):.1f}ms", f"{datos_prueba2.get('latencia_promedio', 0):.1f}ms"],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # 3. Conexiones Exitosas vs Fallidas
        conexiones_exitosas = [datos_prueba1.get('conexiones_exitosas', 0), datos_prueba2.get('conexiones_exitosas', 0)]
        conexiones_fallidas = [datos_prueba1.get('conexiones_fallidas', 0), datos_prueba2.get('conexiones_fallidas', 0)]
        
        fig.add_trace(
            go.Bar(
                x=[nombre_prueba1.replace('_', ' '), nombre_prueba2.replace('_', ' ')],
                y=conexiones_exitosas,
                name='Conexiones Exitosas',
                marker_color='#4ECDC4',
                text=[f"{conexiones_exitosas[0]:,}", f"{conexiones_exitosas[1]:,}"],
                textposition='auto'
            ),
            row=1, col=3
        )
        
        fig.add_trace(
            go.Bar(
                x=[nombre_prueba1.replace('_', ' '), nombre_prueba2.replace('_', ' ')],
                y=conexiones_fallidas,
                name='Conexiones Fallidas',
                marker_color='#FF6B6B',
                text=[f"{conexiones_fallidas[0]:,}", f"{conexiones_fallidas[1]:,}"],
                textposition='auto'
            ),
            row=1, col=3
        )
        
        # 4. Tasa de errores
        tasas_error = []
        for datos_prueba in [datos_prueba1, datos_prueba2]:
            total_errores = datos_prueba.get('total_errores', 0)
            total_requests = datos_prueba.get('total_requests', 1)
            tasa_error = (total_errores / total_requests) * 100
            tasas_error.append(tasa_error)
        
        fig.add_trace(
            go.Bar(
                x=[nombre_prueba1.replace('_', ' '), nombre_prueba2.replace('_', ' ')],
                y=tasas_error,
                name='Tasa de Errores',
                marker_color=['#FFA07A', '#98D8C8'],
                text=[f"{tasas_error[0]:.2f}%", f"{tasas_error[1]:.2f}%"],
                textposition='auto'
            ),
            row=2, col=1
        )
        
        # 5. Percentiles
        percentiles = ['p50', 'p90', 'p95', 'p99']
        prueba1_percs = [datos_prueba1.get('percentiles', {}).get(p, 0) for p in percentiles]
        prueba2_percs = [datos_prueba2.get('percentiles', {}).get(p, 0) for p in percentiles]
        
        fig.add_trace(
            go.Bar(
                x=percentiles,
                y=prueba1_percs,
                name=nombre_prueba1.replace('_', ' '),
                marker_color='#FF6B6B'
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=percentiles,
                y=prueba2_percs,
                name=nombre_prueba2.replace('_', ' '),
                marker_color='#4ECDC4'
            ),
            row=2, col=2
        )
        
        # 6. Total de Requests
        fig.add_trace(
            go.Bar(
                x=[nombre_prueba1.replace('_', ' '), nombre_prueba2.replace('_', ' ')],
                y=[datos_prueba1.get('total_requests', 0), datos_prueba2.get('total_requests', 0)],
                name='Total Requests',
                marker_color=['#95E1D3', '#F38BA8'],
                text=[f"{datos_prueba1.get('total_requests', 0):,}", f"{datos_prueba2.get('total_requests', 0):,}"],
                textposition='auto'
            ),
            row=2, col=3
        )
        
        # 7. Tipos de Errores - Prueba 1
        errores1 = datos_prueba1.get('errores', {})
        if sum(errores1.values()) > 0:
            fig.add_trace(
                go.Pie(
                    labels=['Conexión', 'Lectura', 'Escritura', 'Timeout'],
                    values=[errores1.get('conexion', 0), errores1.get('lectura', 0), errores1.get('escritura', 0), errores1.get('timeout', 0)],
                    name=f"Errores {nombre_prueba1}",
                    title=f"Errores - {nombre_prueba1.replace('_', ' ')}"
                ),
                row=3, col=1
            )
        
        # 8. Distribución de Conexiones - Prueba 2
        if len(self.datos_parseados) >= 2:
            conexiones_data = {
                'Exitosas': datos_prueba2.get('conexiones_exitosas', 0),
                'Fallidas': datos_prueba2.get('conexiones_fallidas', 0)
            }
            fig.add_trace(
                go.Pie(
                    labels=list(conexiones_data.keys()),
                    values=list(conexiones_data.values()),
                    name=f"Conexiones {nombre_prueba2}",
                    title=f"Conexiones - {nombre_prueba2.replace('_', ' ')}"
                ),
                row=3, col=2
            )
        
        # 9. Tabla resumen
        datos_resumen = [
            ['Métrica', nombre_prueba1.replace('_', ' '), nombre_prueba2.replace('_', ' ')],
            ['RPS', f"{datos_prueba1.get('rps_reportado', 0):.1f}", f"{datos_prueba2.get('rps_reportado', 0):.1f}"],
            ['Latencia Prom (ms)', f"{datos_prueba1.get('latencia_promedio', 0):.1f}", f"{datos_prueba2.get('latencia_promedio', 0):.1f}"],
            ['Total Requests', f"{datos_prueba1.get('total_requests', 0):,}", f"{datos_prueba2.get('total_requests', 0):,}"],
            ['Conexiones Exitosas', f"{datos_prueba1.get('conexiones_exitosas', 0):,}", f"{datos_prueba2.get('conexiones_exitosas', 0):,}"],
            ['Conexiones Fallidas', f"{datos_prueba1.get('conexiones_fallidas', 0):,}", f"{datos_prueba2.get('conexiones_fallidas', 0):,}"],
            ['Tasa de Errores (%)', f"{tasas_error[0]:.2f}", f"{tasas_error[1]:.2f}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=datos_resumen[0], fill_color='#4ECDC4', font=dict(color='white', size=12)),
                cells=dict(values=list(zip(*datos_resumen[1:])), fill_color='#F7F7F7', font=dict(size=11))
            ),
            row=3, col=3
        )
        
        fig.update_layout(
            height=1200,
            title_text="Dashboard de Comparación de Pruebas de Carga",
            title_x=0.5,
            title_font_size=24,
            showlegend=True
        )
        
        return fig
    
    def crear_dashboard_prueba_unica(self):
        """Crear dashboard para una sola prueba"""
        nombre_prueba = list(self.datos_parseados.keys())[0]
        datos_prueba = self.datos_parseados[nombre_prueba]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Medidor RPS', 'Estadísticas de Latencia', 'Tasa de Errores', 'Resumen de Rendimiento'],
            specs=[
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "table"}]
            ]
        )
        
        # 1. Medidor RPS
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=datos_prueba.get('rps_reportado', 0),
                title={'text': "Requests/seg"},
                gauge={'axis': {'range': [None, datos_prueba.get('rps_reportado', 0) * 1.2]},
                       'bar': {'color': "#FF6B6B"}}
            ),
            row=1, col=1
        )
        
        # 2. Estadísticas de latencia
        metricas_latencia = ['Promedio', 'Máximo', 'Desv. Estándar']
        valores_latencia = [
            datos_prueba.get('latencia_promedio', 0),
            datos_prueba.get('latencia_max', 0),
            datos_prueba.get('latencia_stdev', 0)
        ]
        
        fig.add_trace(
            go.Bar(
                x=metricas_latencia,
                y=valores_latencia,
                marker_color=['#4ECDC4', '#FFE66D', '#FF6B6B'],
                text=[f"{v:.1f}ms" for v in valores_latencia],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # 3. Tasa de errores
        tasa_error = (datos_prueba.get('total_errores', 0) / datos_prueba.get('total_requests', 1)) * 100
        fig.add_trace(
            go.Bar(
                x=['Tasa de Errores'],
                y=[tasa_error],
                marker_color='#FFA07A',
                text=[f"{tasa_error:.2f}%"],
                textposition='auto'
            ),
            row=2, col=1
        )
        
        # 4. Tabla resumen
        datos_resumen = [
            ['Métrica', 'Valor'],
            ['Total Requests', f"{datos_prueba.get('total_requests', 0):,}"],
            ['Duración', f"{datos_prueba.get('duracion', 0):.1f}s"],
            ['RPS', f"{datos_prueba.get('rps_reportado', 0):.1f}"],
            ['Latencia Prom', f"{datos_prueba.get('latencia_promedio', 0):.1f}ms"],
            ['Tasa de Errores', f"{tasa_error:.2f}%"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=datos_resumen[0], fill_color='#4ECDC4', font=dict(color='white', size=12)),
                cells=dict(values=list(zip(*datos_resumen[1:])), fill_color='#F7F7F7', font=dict(size=11))
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text=f"Resultados de Prueba de Carga - {nombre_prueba.replace('_', ' ')}",
            title_x=0.5,
            title_font_size=20,
            showlegend=False
        )
        
        return fig
    
    def generar_reporte_html(self):
        """Generar reporte HTML completo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        fig = self.crear_graficos_interactivos()
        if not fig:
            return None
        
        chart_html = fig.to_html(include_plotlyjs='cdn', div_id="dashboard")
        
        plantilla_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Resultados de Pruebas de Carga</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .dashboard-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: #333;
            color: white;
            border-radius: 10px;
        }
        .info-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        .info-section h3 {
            color: #667eea;
            margin-top: 0;
        }
        .command-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .metrics-explanation {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .metric-item {
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .metric-title {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .metric-description {
            color: #666;
            font-size: 14px;
        }
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .warning-title {
            font-weight: bold;
            color: #856404;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Dashboard de Pruebas de Carga</h1>
        <p>Análisis Completo de Rendimiento - Generado el {{ timestamp }}</p>
    </div>
    
    <div class="info-section">
        <h3>📋 Información de las Pruebas</h3>
        <p><strong>Comandos ejecutados:</strong></p>
        <div class="command-box">
            wrk -t32 -c50000 -d300s -s get_verify_number_enhanced.lua https://yasta.bancounion.com.bo/gateway/user/verify/number?username=65663503
        </div>
        <div class="command-box">
            wrk -t32 -c50000 -d300s -s post_pagos_enhanced.lua https://ws.pagosbolivia.com.bo:8443/api/pagos/ProcessMessage
        </div>
        <p><strong>Configuración:</strong> 32 threads, 50000 conexiones concurrentes, 300 segundos de duración</p>
    </div>
    
    <div class="info-section">
        <h3>📊 Explicación de Métricas</h3>
        <div class="metrics-explanation">
            <div class="metric-item">
                <div class="metric-title">🚀 Requests por Segundo (RPS)</div>
                <div class="metric-description">Número de peticiones HTTP completadas exitosamente por segundo. Mayor RPS = mejor rendimiento.</div>
            </div>
            
            <div class="metric-item">
                <div class="metric-title">⏱️ Latencia Promedio</div>
                <div class="metric-description">Tiempo promedio que tarda el servidor en responder a una petición (en milisegundos). Menor latencia = respuesta más rápida.</div>
            </div>
            
            <div class="metric-item">
                <div class="metric-title">🔗 Conexiones Exitosas vs Fallidas</div>
                <div class="metric-description">
                    <strong>Exitosas:</strong> Peticiones que se completaron correctamente<br>
                    <strong>Fallidas:</strong> Conexiones que no pudieron establecerse (errores de red, servidor sobrecargado, etc.)
                </div>
            </div>
            
            <div class="metric-item">
                <div class="metric-title">❌ Tasa de Errores</div>
                <div class="metric-description">
                    Porcentaje de errores respecto al total de peticiones. Se calcula: (Total Errores / Total Requests) × 100
                </div>
                <div class="warning-box">
                    <div class="warning-title">⚠️ Importante sobre Tasa de Errores > 100%</div>
                    Si ves una tasa de errores superior al 100% (como 307.04%), significa que hubo más errores de conexión que peticiones exitosas. 
                    Esto ocurre cuando el servidor está sobrecargado y rechaza muchas conexiones antes de procesarlas.
                </div>
            </div>
            
            <div class="metric-item">
                <div class="metric-title">📈 Percentiles de Latencia</div>
                <div class="metric-description">
                    <strong>P50:</strong> 50% de las peticiones tardaron menos que este tiempo<br>
                    <strong>P90:</strong> 90% de las peticiones tardaron menos que este tiempo<br>
                    <strong>P95:</strong> 95% de las peticiones tardaron menos que este tiempo<br>
                    <strong>P99:</strong> 99% de las peticiones tardaron menos que este tiempo
                </div>
            </div>
            
            <div class="metric-item">
                <div class="metric-title">🔧 Tipos de Errores</div>
                <div class="metric-description">
                    <strong>Conexión:</strong> No se pudo conectar al servidor<br>
                    <strong>Lectura:</strong> Error al leer la respuesta<br>
                    <strong>Escritura:</strong> Error al enviar la petición<br>
                    <strong>Timeout:</strong> El servidor tardó demasiado en responder
                </div>
            </div>
            
            <div class="metric-item">
                <div class="metric-title">📊 Total de Requests</div>
                <div class="metric-description">Número total de peticiones HTTP que se completaron exitosamente durante la prueba.</div>
            </div>
        </div>
    </div>
    
    <div class="dashboard-container">
        {{ chart_html }}
    </div>
    
    <div class="footer">
        <p>Generado automáticamente por el Sistema de Análisis de Carga</p>
        <p>Timestamp: {{ timestamp }}</p>
    </div>
</body>
</html>
        """
        
        template = Template(plantilla_html)
        html_final = template.render(
            chart_html=chart_html,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        nombre_archivo_html = f'dashboard_pruebas_carga_{timestamp}.html'
        with open(nombre_archivo_html, 'w', encoding='utf-8') as f:
            f.write(html_final)
        
        print(f"Dashboard HTML guardado como: {nombre_archivo_html}")
        return nombre_archivo_html

def main():
    analizador = AnalizadorHTML()
    
    # Buscar el archivo de resultados más reciente
    archivos_resultados = [f for f in os.listdir('.') if f.startswith('resultados_pruebas_carga_') and f.endswith('.json')]
    
    if not archivos_resultados:
        print("No se encontraron archivos de resultados. Por favor ejecuta las pruebas de carga primero.")
        return
    
    archivo_resultados = sorted(archivos_resultados)[-1]
    print(f"Usando archivo de resultados: {archivo_resultados}")
    
    analizador.cargar_resultados(archivo_resultados)
    
    if not analizador.datos_parseados:
        print("No se encontraron datos válidos en el archivo de resultados.")
        return
    
    print("Generando dashboard HTML...")
    archivo_html = analizador.generar_reporte_html()
    
    if archivo_html:
        print(f"\n¡Dashboard HTML generado exitosamente!")
        print(f"Archivo: {archivo_html}")
        print("Abre este archivo en tu navegador web para ver el dashboard interactivo.")

if __name__ == "__main__":
    main()
