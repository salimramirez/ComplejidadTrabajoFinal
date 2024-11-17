from flask import Blueprint, render_template, request, session, redirect, url_for
from app.database.database import conectar_db
from app.utils.dijkstra import cargar_grafo, calcular_dijkstra, graficar_ruta

buscar_blueprint = Blueprint('buscar', __name__, url_prefix='/buscar')


@buscar_blueprint.route('/', methods=['GET', 'POST'])
def buscar():
    resultados = []
    distancia = None
    ruta = None
    imagen_grafo = None

    # Inicializar sesión para guardar selecciones
    if "origen" not in session:
        session["origen"] = None
    if "destino" not in session:
        session["destino"] = None

    modo = request.form.get('modo', 'origen')  # Determina si seleccionamos origen o destino

    if request.method == 'POST':
        # Buscar aeropuertos por ciudad o país
        criterio = request.form.get('criterio')
        if criterio:
            try:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT iata, nombre, ciudad, pais
                    FROM aeropuertos
                    WHERE ciudad LIKE ? OR pais LIKE ?
                """, (f"%{criterio}%", f"%{criterio}%"))
                resultados = cursor.fetchall()
                conn.close()
            except Exception as e:
                print(f"Error en la búsqueda: {e}")

        # Seleccionar aeropuerto
        aeropuerto = request.form.get('aeropuerto')
        if aeropuerto:
            if modo == 'origen':
                session["origen"] = aeropuerto
            elif modo == 'destino':
                session["destino"] = aeropuerto

        # Si ambos nodos están seleccionados, calcular ruta
        if session["origen"] and session["destino"]:
            try:
                grafo = cargar_grafo()
                distancia, ruta = calcular_dijkstra(grafo, session["origen"], session["destino"])
                imagen_grafo = 'static/img/ruta_buscar.png'
                graficar_ruta(grafo, ruta, output_path=f"app/{imagen_grafo}")
            except Exception as e:
                print(f"Error al calcular la ruta: {e}")
                distancia = None
                ruta = None
                imagen_grafo = None

    return render_template(
        'buscar.html',
        resultados=resultados,
        seleccion={"origen": session["origen"], "destino": session["destino"]},
        modo=modo,
        distancia=distancia,
        ruta=ruta,
        imagen_grafo=imagen_grafo
    )


@buscar_blueprint.route('/reiniciar', methods=['POST'])
def reiniciar():
    """Reinicia la selección de nodos."""
    session["origen"] = None
    session["destino"] = None
    return redirect(url_for('buscar.buscar'))
