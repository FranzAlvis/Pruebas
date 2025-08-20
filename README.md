# Sistema de Pruebas de Carga con Dashboard HTML Interactivo

Este sistema completo te permite ejecutar pruebas de carga con `wrk` y generar **dashboards HTML interactivos** con gráficos detallados. Ahora puedes **seleccionar qué prueba ejecutar** individualmente.

## 🚀 Uso Rápido - Sistema Completo

### Ejecutar TODO Automáticamente
```bash
# Ejecutar ambas pruebas y generar dashboard HTML
python3 sistema_completo_pruebas.py ambas

# Ejecutar solo la prueba GET
python3 sistema_completo_pruebas.py get

# Ejecutar solo la prueba POST
python3 sistema_completo_pruebas.py post
```

## 📁 Archivos del Sistema

### Scripts Lua Mejorados
- `get_verify_number_enhanced.lua` - Prueba GET con métricas detalladas
- `post_pagos_enhanced.lua` - Prueba POST con métricas detalladas

### Scripts de Ejecución
- `sistema_completo_pruebas.py` - **SCRIPT PRINCIPAL** - Ejecuta todo automáticamente
- `ejecutar_pruebas_carga.py` - Ejecutor con selección individual de pruebas
- `generar_reporte_html.py` - Generador de dashboard HTML interactivo

### Scripts Originales (compatibilidad)
- `run_load_tests.py` - Ejecutor original (ambas pruebas)
- `generate_graphics.py` - Generador PNG original

### Configuración
- `requirements.txt` - Dependencias Python (incluye plotly, jinja2)

## 🎯 Comandos Disponibles

### Selección Individual de Pruebas
```bash
# Ver ayuda detallada
python3 ejecutar_pruebas_carga.py

# Ejecutar solo GET
python3 ejecutar_pruebas_carga.py get

# Ejecutar solo POST  
python3 ejecutar_pruebas_carga.py post

# Ejecutar ambas secuencialmente
python3 ejecutar_pruebas_carga.py ambas
```

### Generar Solo el Dashboard HTML
```bash
# Generar dashboard desde resultados existentes
python3 generar_reporte_html.py
```

## 📊 Comandos wrk Incluidos

**GET Verify Number:**
```bash
wrk -t12 -c3000 -d300s -s get_verify_number_enhanced.lua https://yasta.bancounion.com.bo/gateway/user/verify/number?username=65663503
```

**POST Pagos:**
```bash
wrk -t12 -c3000 -d300s -s post_pagos_enhanced.lua https://ws.pagosbolivia.com.bo:8443/api/pagos/ProcessMessage
```

**Configuración:** 12 threads, 3000 conexiones concurrentes, 300 segundos de duración

## 🌐 Dashboard HTML Interactivo

### Archivos Generados
- `resultados_pruebas_carga_YYYYMMDD_HHMMSS.json` - Datos en JSON
- `dashboard_pruebas_carga_YYYYMMDD_HHMMSS.html` - **Dashboard interactivo**

### Gráficos Incluidos en el Dashboard
1. **Requests por Segundo** - Comparación RPS entre pruebas
2. **Latencia Promedio** - Latencia comparativa en ms
3. **Total de Requests** - Requests procesados totales
4. **Tasa de Errores** - Porcentaje de errores
5. **Percentiles de Latencia** - P50, P90, P95, P99
6. **Medidor RPS** - Gauge interactivo (prueba individual)
7. **Tabla Resumen** - Métricas clave organizadas

### Características del Dashboard
- **Interactivo** - Zoom, hover, tooltips
- **Responsive** - Se adapta a cualquier pantalla
- **Moderno** - Diseño profesional con gradientes
- **Detallado** - Información completa de comandos ejecutados

## ⚙️ Instalación y Requisitos

### Dependencias Automáticas
El sistema instala automáticamente:
- matplotlib, seaborn, pandas, numpy
- plotly (gráficos interactivos)
- jinja2 (templates HTML)

### Requisitos del Sistema
- Python 3.6+
- wrk (HTTP benchmarking tool)
- Conexión a internet

## 🔧 Resolución de Problemas

### Errores Comunes
1. **Dependencias faltantes:** El sistema las instala automáticamente
2. **wrk no encontrado:** `sudo apt install wrk` (Ubuntu/Debian)
3. **Archivos Lua faltantes:** Verifica que estén en el directorio
4. **Permisos:** Usar `python3` en lugar de `python`

### Verificación
```bash
# Verificar que wrk esté instalado
wrk --version

# Verificar archivos Lua
ls *.lua

# Ver ayuda del sistema
python3 sistema_completo_pruebas.py
```

## 🎨 Personalización

### Modificar Parámetros wrk
Edita `ejecutar_pruebas_carga.py` en la sección `comandos_disponibles`:
```python
'comando': 'wrk -t12 -c3000 -d300s -s script.lua URL'
#              ^    ^      ^
#           threads conexiones duración
```

### Cambiar URLs
Modifica las URLs en `comandos_disponibles` del mismo archivo.

### Personalizar Dashboard
Edita `generar_reporte_html.py` para:
- Cambiar colores de gráficos
- Modificar layout HTML
- Agregar métricas adicionales

## 📋 Ejemplos de Uso

### Caso 1: Probar solo el endpoint GET
```bash
python3 sistema_completo_pruebas.py get
# Genera: dashboard_pruebas_carga_YYYYMMDD_HHMMSS.html
```

### Caso 2: Comparar ambos endpoints
```bash
python3 sistema_completo_pruebas.py ambas
# Genera: dashboard comparativo con ambas pruebas
```

### Caso 3: Solo generar dashboard desde datos existentes
```bash
python3 generar_reporte_html.py
# Usa el archivo JSON más reciente
```

## 🏆 Ventajas del Nuevo Sistema

- ✅ **Selección individual** de pruebas con argumentos
- ✅ **Dashboard HTML interactivo** en lugar de PNG estático
- ✅ **Instalación automática** de dependencias
- ✅ **Interfaz en español** completa
- ✅ **Compatibilidad** con scripts originales
- ✅ **Gráficos responsive** que se adaptan a cualquier pantalla
