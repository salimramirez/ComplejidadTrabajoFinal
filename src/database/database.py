import sqlite3
import pandas as pd
from utils.calculadora_distancia import calcular_distancia_haversine

# Ruta a tu base de datos
DB_PATH = "src/database/trafico_aereo.db"

# Función para conectar con la base de datos
def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Función para ejecutar un script SQL desde un archivo
def ejecutar_script(script_path):
    conn = conectar_db()
    with open(script_path, 'r') as script:
        conn.executescript(script.read())
    conn.commit()
    conn.close()

# Función para cargar aeropuertos
def cargar_aeropuertos(csv_path):
    conn = conectar_db()
    cursor = conn.cursor()

    # Leer el CSV
    df = pd.read_csv(csv_path)
    df = df[['IATA', 'Name', 'City', 'Country', 'Latitude', 'Longitude']]  # Usar las columnas esperadas

    # Insertar los datos en la base de datos
    for _, row in df.iterrows():
        # Limpiar las comillas del código IATA
        iata = row['IATA'].strip('"').strip('"')  # Quita las comillas si existen
        nombre = row['Name'].strip('"').strip('"')
        ciudad = row['City'].strip('"').strip('"')
        pais = row['Country'].strip('"').strip('"')
        latitud = row['Latitude']
        longitud = row['Longitude']

        print(f"Procesando aeropuerto: {iata}")  # Debugging

        try:
            cursor.execute("""
                INSERT INTO aeropuertos (iata, nombre, ciudad, pais, latitud, longitud)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (iata, nombre, ciudad, pais, latitud, longitud))
        except sqlite3.IntegrityError:
            print(f"Aeropuerto {iata} ya existe, omitiendo...")

    conn.commit()
    conn.close()

def cargar_rutas(csv_path):
    conn = conectar_db()
    cursor = conn.cursor()

    # Leer el archivo CSV
    df = pd.read_csv(csv_path)
    df = df[['Source_Airport', 'Destination_Airport']]  # Filtrar columnas necesarias

    for _, row in df.iterrows():
        origen = row['Source_Airport']
        destino = row['Destination_Airport']
        print(f"Procesando ruta: {origen} -> {destino}")  # Debugging

        # Verificar que origen y destino existan en la tabla aeropuertos
        cursor.execute("SELECT latitud, longitud FROM aeropuertos WHERE iata = ?", (origen,))
        origen_data = cursor.fetchone()

        cursor.execute("SELECT latitud, longitud FROM aeropuertos WHERE iata = ?", (destino,))
        destino_data = cursor.fetchone()

        if origen_data and destino_data:
            latitud_origen, longitud_origen = origen_data
            latitud_destino, longitud_destino = destino_data

            # Calcular la distancia usando Haversine
            distancia = calcular_distancia_haversine(latitud_origen, longitud_origen, latitud_destino, longitud_destino)

            try:
                # Insertar la ruta en la base de datos
                cursor.execute("""
                    INSERT INTO rutas (origen, destino, distancia)
                    VALUES (?, ?, ?)
                """, (origen, destino, distancia))
                print(f"Ruta {origen} -> {destino} insertada con distancia {distancia} km")  # Debugging
            except sqlite3.IntegrityError:
                print(f"Ruta {origen} -> {destino} ya existe, omitiendo...")
        else:
            print(f"Origen o destino no encontrado: {origen} -> {destino}")

    conn.commit()
    conn.close()



# Función auxiliar para obtener un aeropuerto
def obtener_aeropuerto(iata, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aeropuertos WHERE IATA = ?", (iata,))
    return cursor.fetchone()

def limpiar_tablas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rutas")
    cursor.execute("DELETE FROM aeropuertos")
    conn.commit()
    conn.close()
    print("Tablas limpiadas.")

