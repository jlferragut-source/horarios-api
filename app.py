from flask import Flask, jsonify, request
import json
import os
import re
from datetime import datetime
import openpyxl  # Solo para leer Excel, más ligero que pandas

app = Flask(__name__)

def leer_excel_sin_pandas(archivo_path):
    """Lee archivo Excel sin usar pandas"""
    try:
        workbook = openpyxl.load_workbook(archivo_path, data_only=True)
        sheet = workbook.active
        
        datos = []
        for row in sheet.iter_rows(values_only=True):
            datos.append(list(row))
        
        return datos
    except Exception as e:
        print(f"Error leyendo {archivo_path}: {str(e)}")
        return None

def convertir_horarios():
    """Versión simplificada sin pandas"""
    print("🔄 Convirtiendo horarios sin pandas...")
    
    horarios_combinados = {
        "metadata": {"generado_el": datetime.now().isoformat()},
        "schedules": {}
    }
    
    # Buscar archivos Excel
    import glob
    archivos = glob.glob("*.xls") + glob.glob("*.xlsx")
    
    for archivo in archivos:
        try:
            print(f"📖 Procesando: {archivo}")
            datos = leer_excel_sin_pandas(archivo)
            
            if not datos or len(datos) < 2:
                continue
            
            # Procesar datos
            estaciones = [str(cell).strip() if cell else f"Estacion_{i+1}" 
                         for i, cell in enumerate(datos[0])]
            
            horarios = []
            for fila in datos[1:]:
                fila_limpia = []
                for cell in fila:
                    if cell is None:
                        fila_limpia.append(None)
                    else:
                        fila_limpia.append(str(cell).strip())
                horarios.append(fila_limpia)
            
            # Determinar tipo desde nombre de archivo
            nombre = archivo.lower()
            transporte = 'metro' if 'metro' in nombre else 'tren'
            dias = 'lunes_a_viernes' if 'lunes' in nombre and 'viernes' in nombre else 'sabado_domingo'
            direccion = 'ida' if 'ida' in nombre else 'vuelta'
            
            clave = f"{transporte}_{dias}_{direccion}"
            
            horarios_combinados['schedules'][clave] = {
                "archivo": archivo,
                "estaciones": estaciones,
                "horarios": horarios
            }
            
            print(f"✅ {clave}: {len(estaciones)} estaciones")
            
        except Exception as e:
            print(f"❌ Error en {archivo}: {str(e)}")
            continue
    
    return horarios_combinados

@app.route('/')
def home():
    return jsonify({"message": "API Horarios", "status": "online"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port)