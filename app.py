import sqlite3
import os
from flask import Flask, request, jsonify

# ==================== CÓDIGO DE LA API DE FLASK ====================

app = Flask(__name__)

def buscar_horario(transporte, dia, origen, destino):
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    # Esta línea nos ayudará a depurar el problema en los logs de Render
    print(f"Buscando con los parámetros: transporte={transporte}, dia={dia}, origen={origen}, destino={destino}")
    cursor.execute('''
        SELECT hora_salida, hora_llegada
        FROM horarios
        WHERE transporte = ? AND dia = ? AND estacion_salida = ? AND estacion_llegada = ?
    ''', (transporte, dia, origen, destino))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

@app.route('/horarios', methods=['GET'])
def get_horarios():
    transporte = request.args.get('transporte')
    dia = request.args.get('dia')
    origen = request.args.get('origen')
    destino = request.args.get('destino')

    if not all([transporte, dia, origen, destino]):
        return jsonify({"error": "Faltan parámetros de consulta"}), 400

    horarios = buscar_horario(transporte, dia, origen, destino)

    if horarios:
        return jsonify({"horarios_encontrados": horarios})
    else:
        return jsonify({"mensaje": "No se encontraron horarios para esa ruta."})
