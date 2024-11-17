# src/__init__.py

from flask import Flask
from app.utils.grafo_visualizacion import cargar_grafo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Polfer03#'  # Cambia esto por una clave segura
app.secret_key = 'Polfer03#'

# Cargar el grafo global
try:
    grafo = cargar_grafo()
    print(f"Grafo cargado: {grafo.number_of_nodes()} nodos y {grafo.number_of_edges()} aristas")
except ValueError as e:
    print(f"Error al cargar el grafo: {e}")
    grafo = None

# Registro de Blueprints
from app.routes.main import main_blueprint
from app.routes.dijkstra import dijkstra_blueprint
from app.routes.buscar import buscar_blueprint
from app.routes.grafo import grafo_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(dijkstra_blueprint)
app.register_blueprint(buscar_blueprint)
app.register_blueprint(grafo_blueprint)
