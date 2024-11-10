import math

def calcular_distancia_haversine(latitud1, longitud1, latitud2, longitud2):
    """
    Calcula la distancia entre dos puntos en la Tierra dados por su latitud y longitud
    usando la fórmula de Haversine.

    :param latitud1: Latitud del primer punto en grados.
    :param longitud1: Longitud del primer punto en grados.
    :param latitud2: Latitud del segundo punto en grados.
    :param longitud2: Longitud del segundo punto en grados.
    :return: Distancia entre los dos puntos en kilómetros.
    :raises ValueError: Si las coordenadas están fuera de rango.
    """
    # Validar que las latitudes y longitudes estén dentro de los rangos esperados
    if not (-90 <= latitud1 <= 90 and -90 <= latitud2 <= 90):
        raise ValueError("Las latitudes deben estar entre -90 y 90 grados.")
    if not (-180 <= longitud1 <= 180 and -180 <= longitud2 <= 180):
        raise ValueError("Las longitudes deben estar entre -180 y 180 grados.")

    # Convertir grados a radianes
    latitud1, longitud1, latitud2, longitud2 = map(math.radians, [latitud1, longitud1, latitud2, longitud2])

    # Radio de la Tierra en kilómetros
    radio_tierra = 6371.0

    # Diferencias entre latitudes y longitudes
    dlat = latitud2 - latitud1
    dlon = longitud2 - longitud1

    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(latitud1) * math.cos(latitud2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distancia en kilómetros
    distancia = radio_tierra * c
    return distancia
