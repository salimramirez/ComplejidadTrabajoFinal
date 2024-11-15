import tkinter as tk
from tkinter import messagebox
from utils.grafo_visualizacion import cargar_grafo, calcular_dijkstra, mostrar_resultado_dijkstra, visualizar_ruta_en_mapa
from database.database import conectar_db

def abrir_ventana_dijkstra_con_busqueda():
    # Asegúrate de que el grafo esté cargado
    grafo = cargar_grafo()

    origen_seleccionado = None
    destino_seleccionado = None

    def buscar_aeropuerto(entry_busqueda, listbox_resultados):
        criterio = entry_busqueda.get().strip()
        if not criterio:
            messagebox.showwarning("Advertencia", "Debe ingresar una ciudad o país para buscar.")
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

        # Mostrar resultados en la lista
        listbox_resultados.delete(0, tk.END)
        if resultados:
            for iata, nombre, ciudad, pais in resultados:
                listbox_resultados.insert(tk.END, f"{iata} - {nombre} ({ciudad}, {pais})")
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron aeropuertos para el criterio ingresado.")

    def seleccionar_aeropuerto(listbox_resultados, tipo):
        nonlocal origen_seleccionado, destino_seleccionado
        seleccion = listbox_resultados.get(tk.ACTIVE)
        if not seleccion:
            messagebox.showwarning("Advertencia", f"Debe seleccionar un aeropuerto como {tipo}.")
            return None

        # Extraer el código IATA del texto seleccionado
        iata = seleccion.split(" - ")[0]
        messagebox.showinfo("Selección", f"Seleccionaste el aeropuerto {tipo}: {iata}")
        if tipo == "origen":
            origen_seleccionado = iata
        elif tipo == "destino":
            destino_seleccionado = iata
        return iata

    def ejecutar_dijkstra():
        if not origen_seleccionado or not destino_seleccionado:
            messagebox.showwarning("Advertencia", "Debe seleccionar tanto un nodo de origen como uno de destino.")
            return

        try:
            distancia, ruta = calcular_dijkstra(origen_seleccionado, destino_seleccionado)
            mostrar_resultado_dijkstra(distancia, ruta)
            visualizar_ruta_en_mapa(grafo, ruta)  # Mostrar ruta en el mapa
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    # Crear una nueva ventana para el cálculo con un Canvas y un Frame desplazable
    ventana_dijkstra = tk.Toplevel()
    ventana_dijkstra.title("Calcular Ruta con Dijkstra")
    ventana_dijkstra.geometry("700x700")  # Aumenta el tamaño para acomodar scrollbars

    # Canvas y Scrollbar para toda la ventana
    canvas = tk.Canvas(ventana_dijkstra, borderwidth=0)
    scrollbar = tk.Scrollbar(ventana_dijkstra, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Frame desplazable dentro del Canvas
    frame_scrollable = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_scrollable, anchor="nw")

    # Asegurar que el Canvas se actualice al cambiar el tamaño del Frame
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_scrollable.bind("<Configure>", on_frame_configure)

    # Elementos para buscar origen
    tk.Label(frame_scrollable, text="Buscar aeropuerto de origen", font=("Arial", 12, "bold")).pack(pady=10)
    entry_busqueda_origen = tk.Entry(frame_scrollable, font=("Arial", 12))
    entry_busqueda_origen.pack(pady=5)

    listbox_resultados_origen = tk.Listbox(frame_scrollable, font=("Arial", 12), width=50, height=10)
    listbox_resultados_origen.pack(pady=5)

    btn_buscar_origen = tk.Button(
        frame_scrollable,
        text="Buscar Origen",
        command=lambda: buscar_aeropuerto(entry_busqueda_origen, listbox_resultados_origen),
        font=("Arial", 12),
        bg="lightblue"
    )
    btn_buscar_origen.pack(pady=5)

    btn_seleccionar_origen = tk.Button(
        frame_scrollable,
        text="Seleccionar como Origen",
        command=lambda: seleccionar_aeropuerto(listbox_resultados_origen, "origen"),
        font=("Arial", 12),
        bg="lightgreen"
    )
    btn_seleccionar_origen.pack(pady=10)

    # Elementos para buscar destino
    tk.Label(frame_scrollable, text="Buscar aeropuerto de destino", font=("Arial", 12, "bold")).pack(pady=10)
    entry_busqueda_destino = tk.Entry(frame_scrollable, font=("Arial", 12))
    entry_busqueda_destino.pack(pady=5)

    listbox_resultados_destino = tk.Listbox(frame_scrollable, font=("Arial", 12), width=50, height=10)
    listbox_resultados_destino.pack(pady=5)

    btn_buscar_destino = tk.Button(
        frame_scrollable,
        text="Buscar Destino",
        command=lambda: buscar_aeropuerto(entry_busqueda_destino, listbox_resultados_destino),
        font=("Arial", 12),
        bg="lightblue"
    )
    btn_buscar_destino.pack(pady=5)

    btn_seleccionar_destino = tk.Button(
        frame_scrollable,
        text="Seleccionar como Destino",
        command=lambda: seleccionar_aeropuerto(listbox_resultados_destino, "destino"),
        font=("Arial", 12),
        bg="lightgreen"
    )
    btn_seleccionar_destino.pack(pady=10)

    # Botón para calcular Dijkstra
    btn_calcular = tk.Button(
        frame_scrollable,
        text="Calcular Dijkstra",
        command=ejecutar_dijkstra,
        font=("Arial", 14),
        bg="orange"
    )
    btn_calcular.pack(pady=20)

    # Botón para cerrar la ventana
    btn_cerrar = tk.Button(
        frame_scrollable,
        text="Cerrar",
        command=ventana_dijkstra.destroy,
        font=("Arial", 12),
        bg="red"
    )
    btn_cerrar.pack(pady=10)
