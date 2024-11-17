import networkx as nx
import sqlite3
import matplotlib
matplotlib.use('Agg')  # Configura el backend no interactivo antes de importar pyplot
import matplotlib.pyplot as plt
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
    
def graficar_ruta(grafo, ruta, output_path="app/static/img/ruta_dijkstra.png"):

    try:
        plt.figure(figsize=(15, 10))
        
        # Crear el mapa
        mapa = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
        mapa.drawmapboundary(fill_color='lightblue')
        mapa.fillcontinents(color='beige', lake_color='lightblue')
        mapa.drawcoastlines(color='gray')
        mapa.drawcountries(color='black')

        # Obtener las posiciones de los nodos en el mapa
        posiciones = {}
        for nodo in ruta:
            datos = grafo.nodes[nodo]
            x, y = mapa(datos['longitud'], datos['latitud'])
            posiciones[nodo] = (x, y)
            mapa.plot(x, y, 'ro', markersize=8)  # Nodos
            plt.text(x, y, nodo, fontsize=9, ha='right', va='bottom', color='darkblue')  # Código IATA del nodo

        # Dibujar las aristas (ruta mínima)
        for i in range(len(ruta) - 1):
            origen = ruta[i]
            destino = ruta[i + 1]
            x_origen, y_origen = posiciones[origen]
            x_destino, y_destino = posiciones[destino]
            peso = grafo[origen][destino].get('peso', 0)
            mapa.plot([x_origen, x_destino], [y_origen, y_destino], color='blue', linewidth=2)
            mid_x, mid_y = (x_origen + x_destino) / 2, (y_origen + y_destino) / 2
            plt.text(mid_x, mid_y, f"{peso:.3f} km", fontsize=8, ha='center', color='purple')

        # Guardar la imagen
        plt.title("Ruta Mínima entre Nodos")
        plt.savefig(output_path)
        plt.close()
        print(f"Imagen de la ruta guardada en: {output_path}")
    except Exception as e:
        print(f"Error al graficar la ruta: {e}")