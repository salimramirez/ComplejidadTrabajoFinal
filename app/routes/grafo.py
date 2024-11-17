from flask import Blueprint, render_template
from app.utils.grafo_visualizacion import cargar_grafo, mostrar_subgrafo

grafo_blueprint = Blueprint('grafo', __name__, url_prefix='/grafo')

@grafo_blueprint.route('/')
def visualizar_grafo():
    try:
        # Cargar el grafo y guardar un subgrafo como imagen
        grafo = cargar_grafo()
        mostrar_subgrafo("app/static/img/grafo.png", 300)
        return render_template('grafo.html')
    except Exception as e:
        return f"Error al cargar el grafo: {e}"
