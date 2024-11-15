import sqlite3
import networkx as nx

# Ruta a la base de datos SQLite
DB_PATH = "ComplejidadTrabajoFinal/src/database/trafico_aereo.db"

def construir_grafo_desde_db():
    """
    Construye un grafo de NetworkX a partir de la base de datos SQLite.

    :return: Grafo de NetworkX
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear un grafo vacío
    grafo = nx.Graph()

    # Cargar aeropuertos como nodos
    cursor.execute("SELECT iata, nombre, ciudad, latitud, longitud FROM aeropuertos")
    for fila in cursor.fetchall():
        iata, nombre, ciudad, latitud, longitud = fila
        grafo.add_node(iata, nombre=nombre, ciudad=ciudad, latitud=latitud, longitud=longitud)

    # Cargar rutas como aristas con pesos
    cursor.execute("SELECT origen, destino, peso FROM rutas")
    for fila in cursor.fetchall():
        origen, destino, peso = fila
        grafo.add_edge(origen, destino, peso=peso)

    conn.close()
    return grafo

def dijkstra(origen, destino):
    """
    Implementa el algoritmo de Dijkstra para encontrar la ruta más corta
    entre un nodo de origen y un nodo de destino usando el grafo de la base de datos.

    :param origen: Nodo de origen
    :param destino: Nodo de destino
    :return: Tuple (distancia más corta, ruta más corta)
    """
    try:
        # Construir el grafo desde la base de datos
        grafo = construir_grafo_desde_db()

        # Validar si los nodos existen en el grafo
        if origen not in grafo or destino not in grafo:
            raise ValueError("Uno o ambos nodos no existen en el grafo.")

        # Calcular la distancia y la ruta más corta usando NetworkX
        distancia_corta = nx.shortest_path_length(grafo, source=origen, target=destino, weight='peso')
        ruta_corta = nx.shortest_path(grafo, source=origen, target=destino, weight='peso')

        return distancia_corta, ruta_corta

    except nx.NetworkXNoPath:
        # Caso en que no hay un camino entre los nodos
        return None, None
    except ValueError as e:
        # Caso en que uno o ambos nodos no existen en el grafo
        raise e
    except Exception as e:
        # Manejar cualquier otro error inesperado
        raise RuntimeError(f"Error inesperado en el cálculo de Dijkstra: {e}")
