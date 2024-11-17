import networkx as nx
import sqlite3


def conectar_db():
    """Conecta a la base de datos SQLite."""
    conn = sqlite3.connect('app/database/trafico_aereo.db')  # Asegúrate de que la ruta es correcta
    return conn

def cargar_grafo():
    """Carga el grafo desde la base de datos."""
    grafo = nx.Graph()

    conn = conectar_db()
    cursor = conn.cursor()

    # Cargar aeropuertos como nodos
    cursor.execute("SELECT iata, nombre, ciudad, latitud, longitud FROM aeropuertos")
    aeropuertos = cursor.fetchall()
    for aeropuerto in aeropuertos:
        iata, nombre, ciudad, latitud, longitud = aeropuerto
        try:
            latitud = float(latitud)
            longitud = float(longitud)
            grafo.add_node(iata, nombre=nombre, ciudad=ciudad, latitud=latitud, longitud=longitud)
        except (ValueError, TypeError):
            print(f"Error con el aeropuerto {iata}: coordenadas no válidas ({latitud}, {longitud})")

    # Cargar rutas como aristas
    cursor.execute("SELECT origen, destino, distancia FROM rutas")
    rutas = cursor.fetchall()
    for ruta in rutas:
        origen, destino, distancia = ruta
        try:
            distancia = float(distancia)
            if grafo.has_node(origen) and grafo.has_node(destino):
                grafo.add_edge(origen, destino, peso=distancia)
            else:
                print(f"Ruta de {origen} a {destino} contiene nodos inexistentes.")
        except (ValueError, TypeError):
            print(f"Error con la ruta de {origen} a {destino}: distancia no válida ({distancia})")

    conn.close()

    # Verificar que el grafo tenga nodos y aristas
    if grafo.number_of_nodes() == 0 or grafo.number_of_edges() == 0:
        raise ValueError("El grafo no se pudo cargar correctamente. Verifique los datos.")

    return grafo


def calcular_dijkstra(grafo, origen, destino):
    """Calcula la ruta más corta entre origen y destino usando el algoritmo de Dijkstra."""
    if not grafo.has_node(origen) or not grafo.has_node(destino):
        raise ValueError("Uno o ambos nodos no existen en el grafo.")
    
    try:
        distancia = nx.shortest_path_length(grafo, source=origen, target=destino, weight='peso')
        ruta = nx.shortest_path(grafo, source=origen, target=destino, weight='peso')
        return distancia, ruta
    except nx.NetworkXNoPath:
        raise ValueError(f"No existe una ruta válida entre {origen} y {destino}.")
