import math
#s
def calcular_distancia_haversine(latitud1, longitud1, latitud2, longitud2):
    """
    Calcula la distancia entre dos puntos en la Tierra dados por su latitud y longitud
    usando la fórmula de Haversine.
    """
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