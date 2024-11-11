import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def visualizar_ruta_en_mapa(grafo, ruta):
    """
    Muestra un mapa con la ruta calculada, destacando los nodos y las aristas de la ruta.
    :param grafo: Grafo generado con NetworkX.
    :param ruta: Lista de nodos en la ruta óptima.
    """
    if grafo is None or len(ruta) < 2:
        raise ValueError("El grafo no ha sido generado o la ruta es inválida.")

    # Crear el mapa
    plt.figure(figsize=(12, 8))
    mapa = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
    mapa.drawmapboundary(fill_color='lightblue')
    mapa.fillcontinents(color='beige', lake_color='lightblue')
    mapa.drawcoastlines()
    mapa.drawcountries()

    # Coordenadas de los nodos en la ruta
    posiciones = {}
    for nodo in ruta:
        latitud = grafo.nodes[nodo].get('latitud')
        longitud = grafo.nodes[nodo].get('longitud')
        x, y = mapa(longitud, latitud)
        posiciones[nodo] = (x, y)
        mapa.plot(x, y, 'ro', markersize=8)  # Nodos en rojo

    # Dibujar las aristas de la ruta
    for i in range(len(ruta) - 1):
        origen, destino = ruta[i], ruta[i + 1]
        x_origen, y_origen = posiciones[origen]
        x_destino, y_destino = posiciones[destino]
        mapa.plot([x_origen, x_destino], [y_origen, y_destino], color='red', linewidth=2)  # Aristas en rojo

    plt.title("Ruta Calculada en el Mapa")
    plt.show()
