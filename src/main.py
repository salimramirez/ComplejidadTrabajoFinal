import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from grafo_visualizacion import mostrar_mapa, calcular_dijkstra_desde_lima, calcular_dijkstra_ingresado

# Función para mostrar los créditos
def mostrar_creditos():
    # Crear ventana de créditos
    ventana_creditos = tk.Toplevel()
    ventana_creditos.title("Créditos")
    ventana_creditos.geometry("600x400")

    # Título
    titulo_creditos = tk.Label(ventana_creditos, text="Créditos", font=("Arial", 24, "bold"), fg="darkblue")
    titulo_creditos.pack(pady=10)

    # Subtítulo
    subtitulo = tk.Label(ventana_creditos, text="Integrantes", font=("Arial", 16, "italic"), fg="purple")
    subtitulo.pack(pady=10)

    # Contenedor para imágenes y nombres
    frame_integrantes = tk.Frame(ventana_creditos)
    frame_integrantes.pack(pady=20)

    # Información de los integrantes (imágenes y nombres)
    integrantes = [
        {"nombre": "Salim Ramirez", "imagen": "./data/integrante1.png"},
        {"nombre": "Anjali Amaro", "imagen": "./data/integrante2.png"},
        {"nombre": "Paul Sulca", "imagen": "./data/integrante3.png"}
    ]

    for integrante in integrantes:
        # Crear subframe para cada integrante
        subframe = tk.Frame(frame_integrantes)
        subframe.pack(side=tk.LEFT, padx=10)

        # Cargar y mostrar la imagen del integrante
        try:
            img = Image.open(integrante["imagen"])
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            label_imagen = tk.Label(subframe, image=img_tk)
            label_imagen.image = img_tk  # Mantener referencia
            label_imagen.pack()
        except FileNotFoundError:
            tk.Label(subframe, text="Sin imagen", font=("Arial", 10), fg="red").pack()

        # Mostrar el nombre del integrante
        label_nombre = tk.Label(subframe, text=integrante["nombre"], font=("Arial", 12, "bold"), fg="green")
        label_nombre.pack()

    # Botón para cerrar la ventana de créditos
    btn_cerrar = tk.Button(ventana_creditos, text="Cerrar", command=ventana_creditos.destroy, font=("Arial", 12), bg="lightblue")
    btn_cerrar.pack(pady=20)

# Función para abrir la ventana de cálculo de Dijkstra
def abrir_ventana_dijkstra():
    # Crear nueva ventana
    ventana_dijkstra = tk.Toplevel()
    ventana_dijkstra.title("Calcular menor distancia entre dos nodos")
    ventana_dijkstra.geometry("500x300")

    # Título
    titulo = tk.Label(ventana_dijkstra, text="Calcular menor distancia entre dos nodos", font=("Arial", 16, "bold"))
    titulo.pack(pady=10)

    # Subtítulo
    subtitulo = tk.Label(ventana_dijkstra, text="Algoritmo de Dijkstra", font=("Arial", 14, "italic"))
    subtitulo.pack(pady=5)

    # Texto informativo
    texto = tk.Label(
        ventana_dijkstra,
        text="Elija una opción para calcular la menor distancia entre dos nodos y elegir la ruta óptima",
        font=("Arial", 12),
        wraplength=400,
        justify="center"
    )
    texto.pack(pady=20)

    # Contenedor para los botones
    frame_botones = tk.Frame(ventana_dijkstra)
    frame_botones.pack(pady=10)

    # Botón "Calcular desde Lima, Perú"
    btn_desde_lima = tk.Button(
        frame_botones,
        text="Calcular desde Lima, Perú",
        command=calcular_dijkstra_desde_lima,
        font=("Arial", 12),
        bg="lightblue",
        width=20
    )
    btn_desde_lima.pack(side=tk.LEFT, padx=10)

    # Botón "Ingresar un origen"
    btn_ingresar_origen = tk.Button(
        frame_botones,
        text="Ingresar un origen",
        command=calcular_dijkstra_ingresado,
        font=("Arial", 12),
        bg="lightgreen",
        width=20
    )
    btn_ingresar_origen.pack(side=tk.LEFT, padx=10)

    # Botón para cerrar la ventana
    btn_cerrar = tk.Button(ventana_dijkstra, text="Cerrar", command=ventana_dijkstra.destroy, font=("Arial", 12))
    btn_cerrar.pack(pady=20)

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Red de Tráfico Aéreo")
ventana.geometry("800x600")

# Título
titulo = tk.Label(
    ventana, 
    text="Red de Tráfico Aéreo", 
    font=("Century", 28, "bold"),  # Fuente Century, más formal
    fg="darkblue",  # Texto en azul oscuro
    padx=20, 
    pady=10
)

titulo.pack(pady=20)

# Imagen
ruta_imagen = "./data/imagen_principal.png"
try:
    imagen = Image.open(ruta_imagen)
    imagen = imagen.resize((400, 300), Image.Resampling.LANCZOS)
    imagen_tk = ImageTk.PhotoImage(imagen)
    label_imagen = tk.Label(ventana, image=imagen_tk)
    label_imagen.image = imagen_tk  # Referencia para evitar garbage collection
    label_imagen.pack(pady=10)
except FileNotFoundError:
    tk.Label(ventana, text="No se encontró la imagen. Verifica la ruta.", font=("Arial", 12), fg="red").pack(pady=10)

# Botón "Ver Mapa"
btn_ver_mapa = tk.Button(ventana, text="Ver Mapa", command=lambda: mostrar_mapa(ventana), font=("Arial", 14), bg="lightblue")
btn_ver_mapa.pack(pady=10)

# Botón "Calcular Dijkstra"
btn_dijkstra = tk.Button(
    ventana, 
    text="Calcular Dijkstra", 
    command=abrir_ventana_dijkstra, 
    font=("Arial", 14), 
    bg="lightgreen"
)
btn_dijkstra.pack(pady=10)

# Botón "Ver Créditos"
btn_creditos = tk.Button(ventana, text="Ver Créditos", command=mostrar_creditos, font=("Arial", 14), bg="lightyellow")
btn_creditos.pack(pady=10)

# Ejecutar aplicación
ventana.mainloop()
