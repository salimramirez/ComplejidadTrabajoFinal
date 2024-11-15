import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import tkinter as tk
from tkinter import messagebox, simpledialog
from utils.visualizar_grafo_dijkstra import visualizar_ruta_en_mapa

# Ruta a la base de datos
DB_PATH = "src/database/trafico_aereo.db"

grafo = None  # Variable global para almacenar el grafo

# Conexión a la base de datos
def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Cargar grafo desde la base de datos
# Función para cargar el grafo desde la base de datos
def cargar_grafo():
    global grafo
    grafo = nx.Graph()  # Crear un nuevo grafo

    conn = conectar_db()
    cursor = conn.cursor()

    # Cargar aeropuertos
    cursor.execute("SELECT iata, nombre, ciudad, latitud, longitud FROM aeropuertos")
    aeropuertos = cursor.fetchall()
    for aeropuerto in aeropuertos:
        iata, nombre, ciudad, latitud, longitud = aeropuerto
        try:
            # Asegurarse de que latitud y longitud sean float
            latitud = float(latitud)
            longitud = float(longitud)
            grafo.add_node(iata, nombre=nombre, ciudad=ciudad, latitud=latitud, longitud=longitud)
        except ValueError:
            print(f"Error con el aeropuerto {iata}: coordenadas no válidas ({latitud}, {longitud})")

    # Cargar rutas
    cursor.execute("SELECT origen, destino, distancia FROM rutas")
    rutas = cursor.fetchall()
    for ruta in rutas:
        origen, destino, distancia = ruta
        grafo.add_edge(origen, destino, peso=distancia)

    conn.close()

# Mostrar el mapa
def mostrar_mapa(ventana_principal=None):
    if grafo is None:
        cargar_grafo()

    # Crear el mapa
    plt.figure(figsize=(15, 10))
    mapa = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

    mapa.drawmapboundary(fill_color='lightblue')
    mapa.fillcontinents(color='beige', lake_color='lightblue')
    mapa.drawcoastlines(color='gray')
    mapa.drawcountries(color='black')

    # Posiciones para nodos en el mapa
    posiciones = {}
    for nodo, datos in grafo.nodes(data=True):
        x, y = mapa(datos['longitud'], datos['latitud'])
        posiciones[nodo] = (x, y)
        mapa.plot(x, y, 'bo', markersize=5)

    # Dibujar aristas
    for origen, destino, datos in grafo.edges(data=True):
        x_origen, y_origen = posiciones[origen]
        x_destino, y_destino = posiciones[destino]
        mapa.plot([x_origen, x_destino], [y_origen, y_destino], color='blue', linewidth=1)

    # Etiquetas de las aristas (distancias)
    edge_labels = {(origen, destino): f"{datos['peso']} km" for origen, destino, datos in grafo.edges(data=True)}
    nx.draw_networkx_edge_labels(grafo, posiciones, edge_labels=edge_labels, font_size=8, bbox=dict(alpha=0))

    # Dibujar nodos
    nx.draw(grafo, posiciones, with_labels=True, node_size=500, node_color="red", font_size=8, font_weight="bold")

    plt.title("Red de Tráfico Aéreo ")
    plt.show()

# Calcular Dijkstra desde Lima
def calcular_dijkstra_desde_lima():
    if grafo is None:
        cargar_grafo()

    destino = simpledialog.askstring("Nodo de Destino", "Ingrese el nodo de destino (IATA):")

    if not destino:
        messagebox.showwarning("Advertencia", "Debe ingresar un nodo de destino.")
        return

    try:
        distancia, ruta = calcular_dijkstra("LIM", destino)
        mostrar_resultado_dijkstra(distancia, ruta)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Calcular Dijkstra ingresando nodos
def calcular_dijkstra_ingresado():
    if grafo is None:
        cargar_grafo()

    origen = simpledialog.askstring("Nodo de Origen", "Ingrese el nodo de origen (IATA):")
    destino = simpledialog.askstring("Nodo de Destino", "Ingrese el nodo de destino (IATA):")

    if not origen or not destino:
        messagebox.showwarning("Advertencia", "Debe ingresar ambos nodos.")
        return

    try:
        distancia, ruta = calcular_dijkstra(origen, destino)
        mostrar_resultado_dijkstra(distancia, ruta)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Mostrar resultado de Dijkstra
def mostrar_resultado_dijkstra(distancia, ruta):
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

     # Botón para mostrar la ruta en un mapa personalizado
    btn_mapa = tk.Button(
        ventana_resultado,
        text="Visualizar Ruta en Mapa",
        command=lambda: visualizar_ruta_en_mapa(grafo, ruta),
        font=("Arial", 12),
        bg="lightblue"
    )
    btn_mapa.pack(pady=20)  # Agregar al diseño de la ventana

    # Botón para cerrar la ventana
    btn_cerrar = tk.Button(
        ventana_resultado,
        text="Cerrar",
        command=ventana_resultado.destroy,
        font=("Arial", 12),
        bg="lightblue"
    )
    btn_cerrar.pack(pady=20)

# Calcular Dijkstra en el grafo
def calcular_dijkstra(origen, destino):
    if origen not in grafo or destino not in grafo:
        raise ValueError("Uno o ambos nodos no existen en el grafo.")
    
    distancia = nx.shortest_path_length(grafo, source=origen, target=destino, weight='peso')
    ruta = nx.shortest_path(grafo, source=origen, target=destino, weight='peso')
    return distancia, ruta

def buscar_aeropuerto():
    def buscar():
        # Obtener el texto de búsqueda ingresado
        criterio = entry_busqueda.get().strip()
        if not criterio:
            messagebox.showwarning("Advertencia", "Debe ingresar un criterio de búsqueda.")
            return
        
        # Consultar la base de datos
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT iata, nombre, ciudad, pais
            FROM aeropuertos
            WHERE ciudad LIKE ? OR pais LIKE ?
        """, (f"%{criterio}%", f"%{criterio}%"))
        resultados = cursor.fetchall()
        conn.close()

        # Mostrar los resultados en la lista
        listbox_resultados.delete(0, tk.END)
        if resultados:
            for iata, nombre, ciudad, pais in resultados:
                listbox_resultados.insert(tk.END, f"{iata} - {nombre} ({ciudad}, {pais})")
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron aeropuertos para el criterio ingresado.")

    def seleccionar():
        seleccion = listbox_resultados.get(tk.ACTIVE)
        if not seleccion:
            messagebox.showwarning("Advertencia", "Debe seleccionar un aeropuerto.")
            return
        # Extraer el código IATA del texto seleccionado
        iata = seleccion.split(" - ")[0]
        if modo.get() == "origen":
            origen_label.config(text=f"Origen: {iata}")
            seleccionar.origen = iata
        elif modo.get() == "destino":
            destino_label.config(text=f"Destino: {iata}")
            seleccionar.destino = iata
        ventana_busqueda.destroy()

    # Ventana de búsqueda
    ventana_busqueda = tk.Toplevel()
    ventana_busqueda.title("Buscar Aeropuerto")
    ventana_busqueda.geometry("500x400")

    # Widgets de búsqueda
    tk.Label(ventana_busqueda, text="Ingrese ciudad o país:", font=("Arial", 12)).pack(pady=10)
    entry_busqueda = tk.Entry(ventana_busqueda, font=("Arial", 12))
    entry_busqueda.pack(pady=10)
    tk.Button(ventana_busqueda, text="Buscar", command=buscar, font=("Arial", 12), bg="lightblue").pack(pady=10)

    # Lista de resultados
    listbox_resultados = tk.Listbox(ventana_busqueda, font=("Arial", 12), width=50, height=15)
    listbox_resultados.pack(pady=10)

    # Botón de selección
    tk.Button(ventana_busqueda, text="Seleccionar", command=seleccionar, font=("Arial", 12), bg="lightgreen").pack(pady=10)

# Función principal para seleccionar origen y destino
def seleccionar_origen_destino():
    global origen_label, destino_label

    # Ventana principal
    ventana_seleccion = tk.Toplevel()
    ventana_seleccion.title("Seleccionar Origen y Destino")
    ventana_seleccion.geometry("400x300")

    # Etiquetas para mostrar origen y destino seleccionados
    origen_label = tk.Label(ventana_seleccion, text="Origen: No seleccionado", font=("Arial", 12))
    origen_label.pack(pady=10)

    destino_label = tk.Label(ventana_seleccion, text="Destino: No seleccionado", font=("Arial", 12))
    destino_label.pack(pady=10)

    # Botones para buscar origen y destino
    tk.Button(ventana_seleccion, text="Seleccionar Origen", command=lambda: buscar_aeropuerto_config("origen"), font=("Arial", 12), bg="lightblue").pack(pady=10)
    tk.Button(ventana_seleccion, text="Seleccionar Destino", command=lambda: buscar_aeropuerto_config("destino"), font=("Arial", 12), bg="lightblue").pack(pady=10)

    # Botón para continuar
    tk.Button(
        ventana_seleccion,
        text="Calcular Ruta",
        command=lambda: calcular_ruta_dijkstra(ventana_seleccion, seleccionar_origen_destino.origen, seleccionar_origen_destino.destino),
        font=("Arial", 12),
        bg="lightgreen"
    ).pack(pady=20)

    # Variables globales para el origen y destino
    seleccionar_origen_destino.origen = None
    seleccionar_origen_destino.destino = None

# Configurar modo de búsqueda
def buscar_aeropuerto_config(modo_actual):
    global modo
    modo.set(modo_actual)
    buscar_aeropuerto()

# Calcular ruta con los nodos seleccionados
def calcular_ruta_dijkstra(ventana, origen, destino):
    if not origen or not destino:
        messagebox.showwarning("Advertencia", "Debe seleccionar tanto el origen como el destino.")
        return
    try:
        distancia, ruta = calcular_dijkstra(origen, destino)
        mostrar_resultado_dijkstra(distancia, ruta)
        ventana.destroy()
    except ValueError as e:
        messagebox.showerror("Error", str(e))
