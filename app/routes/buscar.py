from flask import Blueprint, render_template, request, redirect, url_for
from app.database.database import conectar_db

buscar_blueprint = Blueprint('buscar', __name__, url_prefix='/buscar')

@buscar_blueprint.route('/', methods=['GET', 'POST'])
def buscar():
    resultados = []
    if request.method == 'POST':
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
    return render_template('buscar.html', resultados=resultados)

@buscar_blueprint.route('/seleccionar', methods=['POST'])
def seleccionar():
    aeropuerto = request.form.get('aeropuerto')
    if aeropuerto:
        return f"Aeropuerto seleccionado: {aeropuerto}"
    return redirect(url_for('buscar.buscar'))
