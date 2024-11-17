# src/routes/dijkstra.py
from flask import Blueprint, render_template, request
from app.utils.dijkstra import calcular_dijkstra, graficar_ruta, cargar_grafo
 # Asegúrate de definir calcular_dijkstra

dijkstra_blueprint = Blueprint('dijkstra', __name__, url_prefix='/dijkstra')

# Cargar el grafo (puede ser global o pasado desde app)
grafo = cargar_grafo()

@dijkstra_blueprint.route('/', methods=['GET', 'POST'])
def calcular_ruta():
    error = None
    distancia = None
    ruta = None
    imagen_grafo = None

    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')

        try:
            distancia, ruta = calcular_dijkstra(grafo, origen, destino)
            # Generar la imagen del camino mínimo
            imagen_grafo = 'static/img/ruta_dijkstra.png'
            graficar_ruta(grafo, ruta, output_path=f"app/{imagen_grafo}")
        except ValueError as e:
            error = str(e)

    return render_template('dijkstra.html', error=error, distancia=distancia, ruta=ruta, imagen_grafo=imagen_grafo)