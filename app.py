from flask import Flask, jsonify, request
import json
import os
import glob
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "API de Horarios de Tren y Metro",
        "status": "online",
        "endpoints": {
            "/health": "Estado del servicio",
            "/horarios": "Lista horarios disponibles", 
            "/consulta": "Consulta horarios (?tipo=metro&dias=lunes_a_viernes&direccion=ida)",
            "/estaciones": "Lista todas las estaciones",
            "/regenerar": "Regenerar datos desde XLS"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/horarios')
def horarios():
    return jsonify({
        "horarios_disponibles": [
            "metro_lunes_a_viernes_ida",
            "metro_lunes_a_viernes_vuelta", 
            "metro_sabado_ida",
            "metro_sabado_vuelta",
            "tren_lunes_a_viernes_ida",
            "tren_lunes_a_viernes_vuelta",
            "tren_sabado_domingo_ida",
            "tren_sabado_domingo_vuelta"
        ]
    })

@app.route('/consulta')
def consulta():
    tipo = request.args.get('tipo')
    dias = request.args.get('dias')
    direccion = request.args.get('direccion')
    estacion = request.args.get('estacion')
    
    return jsonify({
        "parametros": {
            "tipo": tipo,
            "dias": dias,
            "direccion": direccion,
            "estacion": estacion
        },
        "mensaje": "Consulta recibida - Lista para procesar horarios"
    })

@app.route('/estaciones')
def estaciones():
    return jsonify({
        "estaciones": ["Estación Central", "Plaza Mayor", "Calle Sol", "Parque Industrial"]
    })

@app.route('/regenerar')
def regenerar():
    return jsonify({"mensaje": "Regeneración de datos iniciada"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Servidor iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port)
