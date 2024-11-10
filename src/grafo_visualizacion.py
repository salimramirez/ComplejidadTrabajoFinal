import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from mpl_toolkits.basemap import Basemap
from calculadora_distancia import calcular_distancia_haversine
from dijkstra import dijkstra

grafo = None  # Variable global para almacenar el grafo

def mostrar_mapa(ventana_principal=None):  # Aceptar el argumento pero no usarlo
    global grafo
    # Código de la función original (sin cambios)

    # Cargar datos
    archivo_aeropuertos = "data/airports.csv"
    archivo_rutas = "data/routes.csv"
    df_aeropuertos = pd.read_csv(archivo_aeropuertos)
    df_rutas = pd.read_csv(archivo_rutas)

    # Procesamiento de datos (idéntico al código original)
    df_aeropuertos['IATA'] = df_aeropuertos['IATA'].str.replace('"', '').str.strip().str.upper()
    df_rutas['Source_Airport'] = df_rutas['Source_Airport'].str.strip().str.upper()
    df_rutas['Destination_Airport'] = df_rutas['Destination_Airport'].str.strip().str.upper()

    df_aeropuertos['Latitude'] = pd.to_numeric(df_aeropuertos['Latitude'], errors='coerce')
    df_aeropuertos['Longitude'] = pd.to_numeric(df_aeropuertos['Longitude'], errors='coerce')

    df_aeropuertos_america = df_aeropuertos[(df_aeropuertos['Latitude'] >= -60) &
                                            (df_aeropuertos['Latitude'] <= 70) &
                                            (df_aeropuertos['Longitude'] >= -170) &
                                            (df_aeropuertos['Longitude'] <= -30)]

    df_rutas_filtradas = df_rutas[df_rutas['Source_Airport'].isin(df_aeropuertos_america['IATA']) &
                                  df_rutas['Destination_Airport'].isin(df_aeropuertos_america['IATA'])]

    aeropuertos_con_rutas = pd.concat([df_rutas_filtradas['Source_Airport'], df_rutas_filtradas['Destination_Airport']]).unique()
    df_aeropuertos_con_rutas = df_aeropuertos_america[df_aeropuertos_america['IATA'].isin(aeropuertos_con_rutas)]

    df_aeropuertos_limited = df_aeropuertos_con_rutas.head(1500)

    print(f"Cantidad de aeropuertos en América: {len(df_aeropuertos_america)}")
    print(f"Cantidad de aeropuertos que se graficarán: {len(df_aeropuertos_limited)}")

    # Crear grafo
    grafo = nx.Graph()  # Asignar el grafo a la variable global
    for _, aeropuerto in df_aeropuertos_limited.iterrows():
        grafo.add_node(aeropuerto['IATA'], nombre=aeropuerto['Name'], ciudad=aeropuerto['City'],
                       latitud=aeropuerto['Latitude'], longitud=aeropuerto['Longitude'])

    df_rutas_filtradas_limited = df_rutas_filtradas[df_rutas_filtradas['Source_Airport'].isin(df_aeropuertos_limited['IATA']) &
                                                    df_rutas_filtradas['Destination_Airport'].isin(df_aeropuertos_limited['IATA'])]

    for _, ruta in df_rutas_filtradas_limited.iterrows():
        origen = ruta['Source_Airport']
        destino = ruta['Destination_Airport']

        aeropuerto_origen = df_aeropuertos[df_aeropuertos['IATA'] == origen].iloc[0]
        aeropuerto_destino = df_aeropuertos[df_aeropuertos['IATA'] == destino].iloc[0]

        latitud_origen, longitud_origen = float(aeropuerto_origen['Latitude']), float(aeropuerto_origen['Longitude'])
        latitud_destino, longitud_destino = float(aeropuerto_destino['Latitude']), float(aeropuerto_destino['Longitude'])

        distancia = calcular_distancia_haversine(latitud_origen, longitud_origen, latitud_destino, longitud_destino)

        distancia_redondeada = round(distancia, 2)

        grafo.add_edge(origen, destino, peso=distancia_redondeada)

    # Graficar mapa
    plt.figure(figsize=(15, 10))
    mapa = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

    mapa.drawmapboundary(fill_color='lightblue')
    mapa.fillcontinents(color='beige', lake_color='lightblue')
    mapa.drawcoastlines(color='gray')
    mapa.drawcountries(color='black')

    posiciones = {}
    for _, aeropuerto in df_aeropuertos_limited.iterrows():
        x, y = mapa(aeropuerto['Longitude'], aeropuerto['Latitude'])
        posiciones[aeropuerto['IATA']] = (x, y)
        mapa.plot(x, y, 'bo', markersize=5)

    for origen, destino, datos in grafo.edges(data=True):
        x_origen, y_origen = posiciones[origen]
        x_destino, y_destino = posiciones[destino]
        mapa.plot([x_origen, x_destino], [y_origen, y_destino], color='blue', linewidth=1)

    edge_labels = {(origen, destino): f"{datos['peso']} km" for origen, destino, datos in grafo.edges(data=True)}

    nx.draw_networkx_edge_labels(grafo, posiciones, edge_labels=edge_labels, font_size=8, bbox=dict(alpha=0))

    nx.draw(grafo, posiciones, with_labels=True, node_size=500, node_color="red", font_size=8, font_weight="bold")

    plt.title("Red de Tráfico Aéreo en América (1500 Aeropuertos)")
    plt.show()

    print(f"Grafo creado con {grafo.number_of_nodes()} aeropuertos y {grafo.number_of_edges()} aristas.")


def calcular_dijkstra_desde_lima():
    global grafo
    if grafo is None:
        tk.messagebox.showerror("Error", "Debe generar el grafo primero mostrando el mapa.")
        return

    # Nodo de origen fijo (LIM) y destino ingresado por el usuario
    destino = tk.simpledialog.askstring("Nodo de Destino", "Ingrese el nodo de destino (IATA):")

    if not destino:
        tk.messagebox.showwarning("Advertencia", "Debe ingresar un nodo de destino.")
        return

    try:
        distancia, ruta = dijkstra(grafo, "LIM", destino)
        mostrar_resultado_dijkstra(distancia, ruta)
    except ValueError as e:
        tk.messagebox.showerror("Error", str(e))

def calcular_dijkstra_ingresado():
    global grafo
    if grafo is None:
        tk.messagebox.showerror("Error", "Debe generar el grafo primero mostrando el mapa.")
        return

    # Elegir nodo de origen y destino
    origen = tk.simpledialog.askstring("Nodo de Origen", "Ingrese el nodo de origen (IATA):")
    destino = tk.simpledialog.askstring("Nodo de Destino", "Ingrese el nodo de destino (IATA):")

    if not origen or not destino:
        tk.messagebox.showwarning("Advertencia", "Debe ingresar ambos nodos.")
        return

    try:
        distancia, ruta = dijkstra(grafo, origen, destino)
        mostrar_resultado_dijkstra(distancia, ruta)
    except ValueError as e:
        tk.messagebox.showerror("Error", str(e))

def mostrar_resultado_dijkstra(distancia, ruta):
    # Crear una nueva ventana para mostrar los resultados
    ventana_resultado = tk.Toplevel()
    ventana_resultado.title("Resultado de Dijkstra")
    ventana_resultado.geometry("600x400")

    # Título
    titulo = tk.Label(
        ventana_resultado, 
        text="Resultado del Algoritmo de Dijkstra", 
        font=("Arial", 18, "bold"), 
        fg="darkblue"
    )
    titulo.pack(pady=20)

    # Subtítulo
    subtitulo = tk.Label(
        ventana_resultado, 
        text="La ruta más corta y su distancia", 
        font=("Arial", 14, "italic"), 
        fg="purple"
    )
    subtitulo.pack(pady=10)

    # Información de la distancia
    distancia_label = tk.Label(
        ventana_resultado, 
        text=f"Distancia más corta: {distancia:.2f} km", 
        font=("Arial", 14), 
        fg="green"
    )
    distancia_label.pack(pady=10)

    # Detalles de la ruta
    ruta_detallada = "\n".join([f"{nodo} ({grafo.nodes[nodo]['nombre']})" for nodo in ruta])
    ruta_label = tk.Label(
        ventana_resultado, 
        text=f"Ruta óptima:\n{ruta_detallada}", 
        font=("Arial", 12), 
        fg="black",
        justify="left",
        wraplength=500
    )
    ruta_label.pack(pady=10)

    # Botón para cerrar la ventana
    btn_cerrar = tk.Button(
        ventana_resultado, 
        text="Cerrar", 
        command=ventana_resultado.destroy, 
        font=("Arial", 12), 
        bg="lightblue"
    )
    btn_cerrar.pack(pady=20)