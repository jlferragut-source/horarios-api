from flask import Flask, jsonify, request
import pandas as pd
import json
import os
import glob
from datetime import datetime, time
import re

app = Flask(__name__)

# ================= CONVERSIÓN AUTOMÁTICA =================

def convertir_xls_a_json():
    """Convierte automáticamente todos los XLS a JSON combinado"""
    
    # Buscar todos los archivos XLS
    archivos_xls = glob.glob("*.xls") + glob.glob("*.xlsx")
    
    if not archivos_xls:
        return {"error": "No se encontraron archivos XLS/XLSX"}
    
    print(f"📁 Encontrados {len(archivos_xls)} archivos Excel")
    
    horarios_combinados = {
        "metadata": {
            "generado_el": datetime.now().isoformat(),
            "total_archivos": len(archivos_xls),
            "descripcion": "Horarios generados automáticamente desde XLS"
        },
        "schedules": {}
    }
    
    for archivo in archivos_xls:
        try:
            print(f"🔄 Procesando: {archivo}")
            
            # Determinar tipo de horario desde el nombre
            nombre = archivo.lower()
            if 'metro' in nombre:
                transporte = 'metro'
            elif 'tren' in nombre:
                transporte = 'tren'
            else:
                transporte = 'otro'
            
            if 'lunes' in nombre and 'viernes' in nombre:
                dias = 'lunes_a_viernes'
            elif 'sabado' in nombre and 'domingo' in nombre:
                dias = 'sabado_domingo'
            elif 'sabado' in nombre:
                dias = 'sabado'
            elif 'domingo' in nombre:
                dias = 'domingo'
            else:
                dias = 'general'
            
            if 'ida' in nombre:
                direccion = 'ida'
            elif 'vuelta' in nombre:
                direccion = 'vuelta'
            else:
                direccion = 'unknown'
            
            # Leer archivo Excel
            try:
                df = pd.read_excel(archivo, header=None, engine='xlrd')
            except:
                df = pd.read_excel(archivo, header=None, engine='openpyxl')
            
            # Procesar estaciones (primera fila)
            estaciones = []
            for col in df.columns:
                valor = df.iloc[0, col]
                if pd.isna(valor):
                    estaciones.append(f"Estacion_{col+1}")
                else:
                    estacion = str(valor).strip()
                    estacion = re.sub(r'[\n\r\t]', ' ', estacion)
                    estacion = re.sub(r'\s+', ' ', estacion)
                    estaciones.append(estacion)
            
            # Procesar horarios
            horarios = []
            for i in range(1, len(df)):
                fila = df.iloc[i].tolist()
                fila_limpia = []
                
                for valor in fila:
                    if pd.isna(valor):
                        fila_limpia.append(None)
                    else:
                        # Convertir tiempos
                        try:
                            if isinstance(valor, (datetime, time)):
                                fila_limpia.append(valor.strftime('%H:%M'))
                            elif isinstance(valor, (int, float)) and valor < 1:
                                # Tiempo Excel
                                minutos_totales = int(valor * 1440)
                                horas = minutos_totales // 60
                                minutos = minutos_totales % 60
                                fila_limpia.append(f"{horas:02d}:{minutos:02d}")
                            else:
                                fila_limpia.append(str(valor).strip())
                        except:
                            fila_limpia.append(str(valor).strip())
                
                if any(x is not None for x in fila_limpia):
                    horarios.append(fila_limpia)
            
            # Crear clave única
            clave = f"{transporte}_{dias}_{direccion}"
            
            # Agregar al combinado
            horarios_combinados['schedules'][clave] = {
                "archivo_origen": archivo,
                "transporte": transporte,
                "dias": dias,
                "direccion": direccion,
                "estaciones": estaciones,
                "horarios": horarios,
                "total_estaciones": len(estaciones),
                "total_horarios": len(horarios)
            }
            
            print(f"✅ {clave}: {len(estaciones)} estaciones, {len(horarios)} horarios")
            
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {str(e)}")
            continue
    
    # Guardar JSON combinado
    with open('horarios_combinados.json', 'w', encoding='utf-8') as f:
        json.dump(horarios_combinados, f, ensure_ascii=False, indent=2)
    
    print(f"🎉 JSON combinado generado: {len(horarios_combinados['schedules'])} horarios")
    return horarios_combinados

# ================= API WEB =================

# Variable global para los datos
datos_horarios = None

@app.before_first_request
def inicializar():
    """Se ejecuta al iniciar la app"""
    global datos_horarios
    print("🚀 Iniciando API de Horarios...")
    
    # Verificar si ya existe el JSON
    if os.path.exists('horarios_combinados.json'):
        print("📖 Cargando JSON existente...")
        try:
            with open('horarios_combinados.json', 'r', encoding='utf-8') as f:
                datos_horarios = json.load(f)
            print(f"✅ JSON cargado: {len(datos_horarios.get('schedules', {}))} horarios")
        except:
            print("❌ Error cargando JSON, generando nuevo...")
            datos_horarios = convertir_xls_a_json()
    else:
        print("🔄 Generando JSON desde XLS...")
        datos_horarios = convertir_xls_a_json()

@app.route('/')
def home():
    return jsonify({
        "mensaje": "API de Horarios Automática",
        "estado": "online",
        "horarios": len(datos_horarios['schedules']) if datos_horarios else 0,
        "endpoints": {
            "/status": "Estado del sistema",
            "/horarios": "Lista de horarios disponibles",
            "/consulta": "Consulta horarios (?tipo=metro&dias=lunes_a_viernes&direccion=ida)"
        }
    })

@app.route('/status')
def status():
    return jsonify({
        "estado": "online",
        "archivos_xls": len(glob.glob("*.xls") + glob.glob("*.xlsx")),
        "horarios_cargados": len(datos_horarios['schedules']) if datos_horarios else 0,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/horarios')
def listar_horarios():
    if not datos_horarios:
        return jsonify({"error": "Datos no disponibles"}), 500
    
    return jsonify({
        "total": len(datos_horarios['schedules']),
        "horarios": list(datos_horarios['schedules'].keys())
    })

@app.route('/consulta')
def consultar():
    if not datos_horarios:
        return jsonify({"error": "Datos no disponibles"}), 500
    
    tipo = request.args.get('tipo')
    dias = request.args.get('dias')
    direccion = request.args.get('direccion')
    estacion = request.args.get('estacion')
    
    resultados = {}
    
    for clave, horario in datos_horarios['schedules'].items():
        partes = clave.split('_')
        if tipo and partes[0] != tipo:
            continue
        if dias and '_'.join(partes[1:-1]) != dias:
            continue
        if direccion and partes[-1] != direccion:
            continue
        
        if estacion:
            # Buscar estación específica
            if estacion in horario['estaciones']:
                idx = horario['estaciones'].index(estacion)
                tiempos = []
                for fila in horario['horarios']:
                    if idx < len(fila) and fila[idx]:
                        tiempos.append(fila[idx])
                if tiempos:
                    resultados[clave] = {
                        "estacion": estacion,
                        "horarios": tiempos,
                        "transporte": partes[0],
                        "dias": '_'.join(partes[1:-1]),
                        "direccion": partes[-1]
                    }
        else:
            resultados[clave] = horario
    
    return jsonify({
        "parametros": {"tipo": tipo, "dias": dias, "direccion": direccion, "estacion": estacion},
        "resultados": resultados,
        "total": len(resultados)
    })

@app.route('/regenerar')
def regenerar():
    """Forzar regeneración del JSON"""
    global datos_horarios
    datos_horarios = convertir_xls_a_json()
    return jsonify({
        "mensaje": "JSON regenerado",
        "horarios": len(datos_horarios['schedules'])
    })

# ================= EJECUCIÓN =================

if __name__ == '__main__':
    # Inicializar datos al empezar
    if not os.path.exists('horarios_combinados.json'):
        print("🔄 Generando horarios_combinados.json por primera vez...")
        convertir_xls_a_json()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Servidor iniciando en puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
