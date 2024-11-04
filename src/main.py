import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from calculadora_distancia import calcular_distancia_haversine

archivo_aeropuertos = "data/airports.csv"
archivo_rutas = "data/routes.csv"
#asd
df_aeropuertos = pd.read_csv(archivo_aeropuertos)
df_rutas = pd.read_csv(archivo_rutas) 

df_aeropuertos['IATA'] = df_aeropuertos['IATA'].str.replace('"', '').str.strip().str.upper()
df_rutas['Source_Airport'] = df_rutas['Source_Airport'].str.strip().str.upper()
df_rutas['Destination_Airport'] = df_rutas['Destination_Airport'].str.strip().str.upper()

df_aeropuertos['Latitude'] = pd.to_numeric(df_aeropuertos['Latitude'], errors='coerce')
df_aeropuertos['Longitude'] = pd.to_numeric(df_aeropuertos['Longitude'], errors='coerce')

df_aeropuertos_america = df_aeropuertos[(df_aeropuertos['Latitude'] >= -60) & 
                                        (df_aeropuertos['Latitude'] <= 70) &
                                        (df_aeropuertos['Longitude'] >= -170) &
                                        (df_aeropuertos['Longitude'] <= -30)]

df_rutas_filtradas = df_rutas[df_rutas['Source_Airport'].isin(df_aeropuertos_america['IATA']) &
                              df_rutas['Destination_Airport'].isin(df_aeropuertos_america['IATA'])]

aeropuertos_con_rutas = pd.concat([df_rutas_filtradas['Source_Airport'], df_rutas_filtradas['Destination_Airport']]).unique()
df_aeropuertos_con_rutas = df_aeropuertos_america[df_aeropuertos_america['IATA'].isin(aeropuertos_con_rutas)]

df_aeropuertos_limited = df_aeropuertos_con_rutas.head(1500)

print(f"Cantidad de aeropuertos en América: {len(df_aeropuertos_america)}")
print(f"Cantidad de aeropuertos que se graficarán: {len(df_aeropuertos_limited)}")

grafo = nx.Graph()

for _, aeropuerto in df_aeropuertos_limited.iterrows():
    grafo.add_node(aeropuerto['IATA'], nombre=aeropuerto['Name'], ciudad=aeropuerto['City'], latitud=aeropuerto['Latitude'], longitud=aeropuerto['Longitude'])

df_rutas_filtradas_limited = df_rutas_filtradas[df_rutas_filtradas['Source_Airport'].isin(df_aeropuertos_limited['IATA']) &
                                                df_rutas_filtradas['Destination_Airport'].isin(df_aeropuertos_limited['IATA'])]

for _, ruta in df_rutas_filtradas_limited.iterrows():
    origen = ruta['Source_Airport']
    destino = ruta['Destination_Airport']

    aeropuerto_origen = df_aeropuertos[df_aeropuertos['IATA'] == origen].iloc[0]
    aeropuerto_destino = df_aeropuertos[df_aeropuertos['IATA'] == destino].iloc[0]

    latitud_origen, longitud_origen = float(aeropuerto_origen['Latitude']), float(aeropuerto_origen['Longitude'])
    latitud_destino, longitud_destino = float(aeropuerto_destino['Latitude']), float(aeropuerto_destino['Longitude'])

    distancia = calcular_distancia_haversine(latitud_origen, longitud_origen, latitud_destino, longitud_destino)

    distancia_redondeada = round(distancia, 2)

    grafo.add_edge(origen, destino, peso=distancia_redondeada)

plt.figure(figsize=(15, 10))
mapa = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

mapa.drawmapboundary(fill_color='lightblue')
mapa.fillcontinents(color='beige', lake_color='lightblue') 
mapa.drawcoastlines(color='gray')
mapa.drawcountries(color='black')  

posiciones = {}
for _, aeropuerto in df_aeropuertos_limited.iterrows():
    x, y = mapa(aeropuerto['Longitude'], aeropuerto['Latitude'])
    posiciones[aeropuerto['IATA']] = (x, y)
    mapa.plot(x, y, 'bo', markersize=5)

for origen, destino, datos in grafo.edges(data=True):
    x_origen, y_origen = posiciones[origen]
    x_destino, y_destino = posiciones[destino]
    mapa.plot([x_origen, x_destino], [y_origen, y_destino], color='blue', linewidth=1)

edge_labels = { (origen, destino): f"{datos['peso']} km" for origen, destino, datos in grafo.edges(data=True) }

nx.draw_networkx_edge_labels(grafo, posiciones, edge_labels=edge_labels, font_size=8, bbox=dict(alpha=0))

nx.draw(grafo, posiciones, with_labels=True, node_size=500, node_color="red", font_size=8, font_weight="bold")

plt.title("Red de Tráfico Aéreo en América (1500 Aeropuertos)")
plt.show()

print(f"Grafo creado con {grafo.number_of_nodes()} aeropuertos y {grafo.number_of_edges()} aristas.")