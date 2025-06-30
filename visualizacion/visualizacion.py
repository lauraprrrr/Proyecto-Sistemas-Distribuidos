import time
import pandas as pd
from elasticsearch import Elasticsearch, ConnectionError
import subprocess
import os

HDFS_FILE_PATH = "/user/proyecto/input/datos_filtrados2.csv"
LOCAL_TMP_PATH = "/tmp/datos_filtrados2.csv"
INDEX_NAME = "alertas_waze_v2"


es = Elasticsearch("http://elasticsearch:9200")

for _ in range(10):
    try:
        if es.ping():
            print("Elasticsearch disponible")
            break
    except ConnectionError:
        pass
    print("Esperando a Elasticsearch...")
    time.sleep(3)
else:
    print("No se pudo conectar a Elasticsearch.")
    exit(1)


try:
    print(f"Recuperando {HDFS_FILE_PATH} desde HDFS")
    subprocess.run(["hdfs", "dfs", "-get", HDFS_FILE_PATH, LOCAL_TMP_PATH], check=True)
    print(f"Archivo descargado localmente en {LOCAL_TMP_PATH}")
except subprocess.CalledProcessError as e:
    print("❌ Error al extraer archivo de hdfs", e)
    exit(1)


try:
    df = pd.read_csv(LOCAL_TMP_PATH)
    print(f"Archivo leído, {len(df)} filas encontradas.")
except Exception as e:
    print("❌ Error al leer el CSV:", e)
    exit(1)


if not es.indices.exists(index=INDEX_NAME):
    print(f"Creando índice '{INDEX_NAME}' en Elastic...")
    es.indices.create(index=INDEX_NAME)


for i, row in df.iterrows():
    try:
        doc = row.to_dict()
        es.index(index=INDEX_NAME, document=doc)
    except Exception as e:
        print(f"❌ Error al indexar fila {i}:", e)

print(f"Indexación completa de {len(df)} documentos en el índice '{INDEX_NAME}'")


time.sleep(180);
