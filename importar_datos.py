import sqlite3
import pandas as pd
import os

def crear_db():
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS horarios (
            transporte TEXT,
            dia TEXT,
            direccion TEXT,
            estacion_salida TEXT,
            hora_salida TEXT,
            estacion_llegada TEXT,
            hora_llegada TEXT
        )
    ''')
    conn.commit()
    conn.close()

def importar_horarios_tren(nombre_archivo, dia, direccion):
    conn = sqlite3.connect('horarios.db')
    ruta_archivo = os.path.join('data', nombre_archivo)
    try:
        df = pd.read_excel(ruta_archivo, header=None).fillna('')
        estaciones = df.iloc[0, 1:].tolist()
        for _, row in df.iloc[1:].iterrows():
            tiempos_trayecto = row[1:].tolist()
            for i in range(len(tiempos_trayecto) - 1):
                hora_salida = str(tiempos_trayecto[i]).strip()
                hora_llegada = str(tiempos_trayecto[i+1]).strip()
                estacion_salida = str(estaciones[i]).strip()
                estacion_llegada = str(estaciones[i+1]).strip()
                if hora_salida and hora_llegada:
                    conn.execute('''
                        INSERT INTO horarios VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', ('tren', dia, direccion, estacion_salida, hora_salida, estacion_llegada, hora_llegada))
        conn.commit()
        print(f"Archivo {nombre_archivo} procesado para tren.")
    except Exception as e:
        print(f"Error al procesar el archivo {nombre_archivo}: {e}")
    finally:
        conn.close()

def importar_horarios_metro(nombre_archivo, dia, direccion):
    conn = sqlite3.connect('horarios.db')
    ruta_archivo = os.path.join('data', nombre_archivo)
    try:
        df = pd.read_excel(ruta_archivo)
        df.columns = ['estacion_salida', 'hora_salida', 'estacion_llegada', 'hora_llegada']
        df['transporte'] = 'metro'
        df['dia'] = dia
        df['direccion'] = direccion
        df.to_sql('horarios', conn, if_exists='append', index=False)
        print(f"Archivo {nombre_archivo} procesado para metro.")
    except Exception as e:
        print(f"Error al procesar el archivo {nombre_archivo}: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    crear_db()
    importar_horarios_tren('TREN LUNES A VIERNES IDA.xls', 'lunes-viernes', 'ida')
    importar_horarios_tren('TREN LUNES A VIERNES VUELTA.xls', 'lunes-viernes', 'vuelta')
    importar_horarios_tren('TREN SABADO DOMINGO IDA.xls', 'sabado-domingo', 'ida')
    importar_horarios_tren('TREN SABADO DOMINGO VUELTA.xls', 'sabado-domingo', 'vuelta')
    importar_horarios_metro('METRO LUNES A VIERNES IDA.xls', 'lunes-viernes', 'ida')
    importar_horarios_metro('METRO LUNES A VIERNES VUELTA.xls', 'lunes-viernes', 'vuelta')
    importar_horarios_metro('METRO SABADO IDA.xls', 'sabado', 'ida')
    importar_horarios_metro('METRO SABADO VUELTA.xls', 'sabado', 'vuelta')
