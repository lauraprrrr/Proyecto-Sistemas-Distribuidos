import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import os
import fiona
import subprocess
from sklearn.cluster import DBSCAN
from math import radians
import time
import geopandas as gpd
from shapely.geometry import Point

#Cargar datos del mongo
client = MongoClient(
    host=os.getenv("MONGO_HOST", "almacenamiento"),
    port=int(os.getenv("MONGO_PORT", 27017)),
    username=os.getenv("MONGO_USER", "root"),
    password=os.getenv("MONGO_PASS", "example"),
    authSource="admin"
)
collection = client.trafico.alertas
docs = list(collection.find())
df = pd.DataFrame(docs)


df = df.dropna(subset=["tipo", "timestamp", "ubicacion"])
df = df[df["ubicacion"].apply(lambda x: isinstance(x, dict) and "coordinates" in x)]
df["latitud"] = df["ubicacion"].apply(lambda x: x["coordinates"][1])
df["longitud"] = df["ubicacion"].apply(lambda x: x["coordinates"][0])
df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")

df = df.dropna(subset=["timestamp_dt"])
df["timestamp_epoch"] = df["timestamp_dt"].astype("int64") // 1_000_000_000
df["timestamp"] = df["timestamp_dt"].dt.strftime("%Y-%m-%d %H:%M:%S")



time.sleep(100)

print("Cargando polígonos comunales...")
fiona.supported_drivers['ESRI Shapefile'] = 'rw'
gdf_comunas = gpd.read_file("shapefiles/comunas/COMUNAS_v1.shp", encoding='latin1')
gdf_comunas = gdf_comunas.to_crs(epsg=4326)

print(gdf_comunas["COMUNA"].unique())


print("Asignando comunas por ubicación geográfica...")
df["geometry"] = df.apply(lambda row: Point(row["longitud"], row["latitud"]), axis=1)
gdf_eventos = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
gdf_resultado = gpd.sjoin(gdf_eventos, gdf_comunas[["COMUNA", "geometry"]], how="left", predicate="within")
df["comuna"] = gdf_resultado["COMUNA"].fillna("Desconocida")


sin_comuna = df["comuna"].eq("Desconocida").sum()
print(f"!!!!!!!!!!!{sin_comuna} registros quedaron sin comuna asignada.")

df["tipo_incidente"] = df["tipo"].str.upper().str.strip()
df["descripcion"] = df["subtype"].fillna("").str.upper().str.replace("_", " ")



filtrados = []

for (tipo, comuna), grupo in df.groupby(["tipo_incidente", "comuna"]):
    if grupo.empty:
        continue

    grupo = grupo.copy()
    grupo["lat_rad"] = grupo["latitud"].apply(radians)
    grupo["lon_rad"] = grupo["longitud"].apply(radians)
    grupo["ts_scaled"] = (grupo["timestamp_epoch"] - grupo["timestamp_epoch"].min()) / (30 * 60) 

    coords = np.hstack([
        grupo[["lat_rad", "lon_rad"]].to_numpy(),
        grupo["ts_scaled"].to_numpy().reshape(-1, 1)
    ])

    clustering = DBSCAN(eps=0.01, min_samples=1, metric='euclidean').fit(coords)
    grupo["grupo"] = clustering.labels_
    deduplicados = grupo.groupby("grupo").first().reset_index()
    filtrados.append(deduplicados)

df_final = pd.concat(filtrados)


# FORMATO PARA Q LO ACEPTE KIBANA!!!!!
df_final["timestamp"] = pd.to_datetime(df_final["timestamp"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
final = df_final[["tipo_incidente", "comuna", "timestamp", "descripcion", "latitud", "longitud"]]
final = final.fillna("").sort_values(by="timestamp")

# Eliminar NaNs numéricos
final = final.dropna(subset=["latitud", "longitud"])
final = final.fillna("")  # rellena strings vacíos donde falten textos

local_path = "/tmp/datos_filtrados5.csv"
hdfs_path = "/user/proyecto/input/datos_filtrados5.csv"

final.to_csv(local_path, index=False)
print(f"\n✅ {len(final)} registros exportados a {local_path}")

print("\nPrimeras 10 filas del CSV:")
try:
    with open(local_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            print(line.strip())
            if i == 10:
                break
except Exception as e:
    print("❌ Error al leer el CSV:", e)

try:
    subprocess.run(["hdfs", "dfs", "-mkdir", "-p", "/user/proyecto/input"], check=True)
    subprocess.run(["hdfs", "dfs", "-put", "-f", local_path, hdfs_path], check=True)
    print(f"\n✅ Archivo subido a HDFS: {hdfs_path}")
except subprocess.CalledProcessError as e:
    print("❌ Error al subir a HDFS:", e)
