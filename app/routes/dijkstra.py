# src/routes/dijkstra.py
from flask import Blueprint, render_template, request
from app.utils.grafo_visualizacion import cargar_grafo, generar_mapa_ruta
from app.utils.dijkstra import calcular_dijkstra 
 # Asegúrate de definir calcular_dijkstra

dijkstra_blueprint = Blueprint('dijkstra', __name__, url_prefix='/dijkstra')

# Cargar el grafo (puede ser global o pasado desde app)
grafo = cargar_grafo()

@dijkstra_blueprint.route('/', methods=['GET', 'POST'])
def calcular_ruta():
    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        try:
            distancia, ruta = calcular_dijkstra(grafo, origen, destino)
             # Generar el mapa con la ruta resaltada
            ruta_mapa = "app/static/img/ruta_dijkstra.png"
            generar_mapa_ruta(grafo, ruta, ruta_mapa)
            return render_template('dijkstra.html', distancia=distancia, ruta=ruta)
        except ValueError as e:
            return render_template('dijkstra.html', error=str(e))
    return render_template('dijkstra.html')
