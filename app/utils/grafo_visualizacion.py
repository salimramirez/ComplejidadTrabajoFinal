import networkx as nx
import sqlite3
import matplotlib.pyplot as plt
import random
from mpl_toolkits.basemap import Basemap


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


def mostrar_subgrafo(grafo, ruta="app/static/img/grafo.png", num_nodos=50):
    """
    Muestra un subgrafo conectado con al menos 'num_nodos' nodos y guarda el resultado como imagen PNG.
    """
    try:
        # Asegurarse de que hay suficientes nodos y aristas
        if grafo.number_of_nodes() == 0 or grafo.number_of_edges() == 0:
            raise ValueError("El grafo no contiene nodos o aristas.")

        # Buscar un componente conectado con suficientes nodos
        for componente in nx.connected_components(grafo):
            if len(componente) >= num_nodos - 10:
                nodos_conectados = list(componente)
                break
        else:
            raise ValueError(f"No hay componentes conectados con al menos {num_nodos} nodos.")

        # Seleccionar los primeros 'num_nodos' nodos del componente conectado
        nodos_seleccionados = random.sample(nodos_conectados, num_nodos)
        subgrafo = grafo.subgraph(nodos_seleccionados)

        # Crear el fondo del mapa con Basemap
        plt.figure(figsize=(15, 10))
        mapa = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
        mapa.drawmapboundary(fill_color='lightblue')
        mapa.fillcontinents(color='beige', lake_color='lightblue')
        mapa.drawcoastlines(color='gray')
        mapa.drawcountries(color='black')

        # Obtener las posiciones de los nodos en el mapa
        posiciones = {}
        for nodo, datos in subgrafo.nodes(data=True):
            x, y = mapa(datos['longitud'], datos['latitud'])
            posiciones[nodo] = (x, y)
            mapa.plot(x, y, 'ro', markersize=8)  # Nodos
            plt.text(x, y, nodo, fontsize=9, ha='right', va='bottom', color='darkblue')  # Código IATA del nodo

        # Dibujar las aristas
        for origen, destino, datos in subgrafo.edges(data=True):
            try:
                # Obtener las posiciones de los nodos
                x_origen, y_origen = posiciones[origen]
                x_destino, y_destino = posiciones[destino]

                # Obtener el peso de la arista
                peso = datos.get('peso', 0)  # Acceso correcto al peso de la arista
                peso = round(peso, 3)  # Redondear el peso a 3 decimales

                # Dibujar la arista
                mapa.plot([x_origen, x_destino], [y_origen, y_destino], color='blue', linewidth=1)

                # Calcular la posición intermedia para colocar el peso
                mid_x, mid_y = (x_origen + x_destino) / 2, (y_origen + y_destino) / 2

                # Dibujar el peso en la posición intermedia
                plt.text(mid_x, mid_y, f"{peso} km", fontsize=8, ha='center', color='black')

            except KeyError as e:
                print(f"Error: No se encontró la posición para los nodos {origen} o {destino}: {e}")

        plt.title("Subgrafo Conectado con Fondo de Mapa", fontsize=14)
        plt.savefig(ruta)
        plt.close()
        print(f"Grafo conectado guardado como imagen en: {ruta}")
    except Exception as e:
        print(f"Error al guardar el subgrafo conectado: {e}")

def generar_mapa_ruta(grafo, ruta, ruta_imagen="app/static/img/ruta_dijkstra.png"):
    """
    Genera un mapa con la ruta mínima resaltada y lo guarda como imagen PNG.
    """
    plt.figure(figsize=(15, 10))
    mapa = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90,
                  llcrnrlon=-180, urcrnrlon=180, resolution='c')
    mapa.drawmapboundary(fill_color='lightblue')
    mapa.fillcontinents(color='beige', lake_color='lightblue')
    mapa.drawcoastlines(color='gray')
    mapa.drawcountries(color='black')

    # Obtener posiciones de los nodos
    posiciones = {}
    for nodo, datos in grafo.nodes(data=True):
        x, y = mapa(datos['longitud'], datos['latitud'])
        posiciones[nodo] = (x, y)
        mapa.plot(x, y, 'ro', markersize=8)  # Nodos
        plt.text(x, y, nodo, fontsize=9, ha='right', va='bottom', color='darkblue')  # Código IATA del nodo

    # Dibujar la ruta
    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]
        x_origen, y_origen = posiciones[origen]
        x_destino, y_destino = posiciones[destino]
        peso = grafo[origen][destino].get('peso', 0)
        peso = round(peso, 3)  # Redondear a 3 decimales

        # Dibujar línea entre nodos de la ruta
        mapa.plot([x_origen, x_destino], [y_origen, y_destino],
                  color='green', linewidth=2, marker='o')

        # Calcular posición intermedia para el peso
        mid_x, mid_y = (x_origen + x_destino) / 2, (y_origen + y_destino) / 2
        plt.text(mid_x, mid_y, f"{peso} km", fontsize=8, ha='center', color='purple')

    plt.title("Ruta Mínima con Algoritmo de Dijkstra", fontsize=14)
    plt.savefig(ruta_imagen)
    plt.close()
    print(f"Ruta de Dijkstra guardada como imagen en: {ruta_imagen}")