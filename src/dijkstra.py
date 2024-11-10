import networkx as nx

def dijkstra(grafo, origen, destino):
    """
    Implementa el algoritmo de Dijkstra para encontrar la ruta más corta
    entre un nodo de origen y un nodo de destino en un grafo.

    :param grafo: Grafo de NetworkX
    :param origen: Nodo de origen
    :param destino: Nodo de destino
    :return: Tuple (distancia más corta, ruta más corta)
    """
    try:
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
