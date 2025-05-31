import requests
import hashlib
from datetime import datetime
from pymongo import MongoClient, IndexModel, ASCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure
import time
import os
import itertools
import random
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

REGION_METROPOLITANA = {
    "top": -33.2993,    # Norte:
    "bottom": -33.6235,  # Sur
    "left": -70.9500,    # Oeste
    "right": -70.3500    # Este
}

GRID_STEPS = int(os.getenv("GRID_STEPS", 5))  
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 8))  
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 25))  

MONGO_CONFIG = {
    "host": os.getenv("MONGO_HOST", "almacenamiento"),
    "port": int(os.getenv("MONGO_PORT", 27017)),
    "username": os.getenv("MONGO_USER", "root"),
    "password": os.getenv("MONGO_PASS", "example"),
    "authSource": "admin",
    "serverSelectionTimeoutMS": 5000,
    "authMechanism": "SCRAM-SHA-256"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Referer": "https://www.waze.com/live-map/"
}

def generar_grid():
    """Genera una cuadrícula de coordenadas con validaciones"""
    
    if (REGION_METROPOLITANA["top"] <= REGION_METROPOLITANA["bottom"] or
        REGION_METROPOLITANA["right"] <= REGION_METROPOLITANA["left"]):
        raise ValueError("Coordenadas de región inválidas")
    
    lat_step = (REGION_METROPOLITANA["top"] - REGION_METROPOLITANA["bottom"]) / GRID_STEPS
    lon_step = (REGION_METROPOLITANA["right"] - REGION_METROPOLITANA["left"]) / GRID_STEPS
    
    
    MIN_GRID_SIZE = 0.015  
    if lat_step < MIN_GRID_SIZE or lon_step < MIN_GRID_SIZE:
        raise ValueError(f"Grids demasiado pequeños (lat: {lat_step:.4f}°, lon: {lon_step:.4f}°). Reduce GRID_STEPS")
    
    grids = []
    for i, j in itertools.product(range(GRID_STEPS), repeat=2):
        grid = {
            "top": round(REGION_METROPOLITANA["top"] - i * lat_step, 6),
            "bottom": round(REGION_METROPOLITANA["top"] - (i + 1) * lat_step, 6),
            "left": round(REGION_METROPOLITANA["left"] + j * lon_step, 6),
            "right": round(REGION_METROPOLITANA["left"] + (j + 1) * lon_step, 6)
        }
        grids.append(grid)
    return grids

def generar_id_unico(alerta):
    """Genera un ID único con hash SHA-256"""
    try:
        hash_input = f"{alerta['type']}-{alerta['location']['x']}-{alerta['location']['y']}-{alerta['pubMillis']}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    except KeyError as e:
        logging.error(f"Error generando ID: {str(e)}")
        raise

def obtener_alertas_grid(grid):
    """Obtiene alertas con manejo de errores mejorado"""
    url = (
        "https://www.waze.com/live-map/api/georss"
        f"?top={min(grid['top'], grid['bottom'])}"
        f"&bottom={max(grid['bottom'], grid['top'])}"
        f"&left={min(grid['left'], grid['right'])}"
        f"&right={max(grid['right'], grid['left'])}"
        "&env=row&types=alerts"
    )
    
    for retry in range(1, 6):  
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                params={"_": int(time.time())}  
            )
            
            if response.status_code == 429: 
                wait_time = 2 ** retry + random.uniform(0, 1)
                logging.warning(f"Rate limit excedido. Reintento {retry} en {wait_time:.1f}s")
                time.sleep(wait_time)
                continue
                
            if response.status_code != 200:
                logging.warning(f"HTTP {response.status_code} en grid {grid}")
                return []
                
            return response.json().get("alerts", [])
            
        except requests.exceptions.Timeout:
            logging.error(f"Timeout en grid {grid}")
            return []
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            logging.error(f"Error en grid {grid} (reintento {retry}): {str(e)}")
            time.sleep(1 + random.random())
    
    return []

def procesar_alerta(alerta, collection):
    """Procesa y guarda una alerta con manejo de errores"""
    try:
        doc = {
            "_id": generar_id_unico(alerta),
            "tipo": alerta['type'],
            "subtype": alerta.get("subtype"),
            "ubicacion": {
                "type": "Point",
                "coordinates": [
                    round(alerta['location']['x'], 6),
                    round(alerta['location']['y'], 6)
                ]
            },
            "timestamp": datetime.utcfromtimestamp(alerta['pubMillis'] / 1000),
            "actualizado": datetime.utcnow(),
            "detalles": {
                "confidence": alerta.get("confidence"),
                "reliability": alerta.get("reliability"),
                "reportRating": alerta.get("reportRating")
            }
        }
        
        result = collection.update_one(
            {"_id": doc["_id"]},
            {"$setOnInsert": doc},
            upsert=True
        )
        return result.upserted_id is not None
        
    except Exception as e:
        logging.error(f"Error procesando alerta: {str(e)}")
        return False

def inicializar_mongodb(collection):
    """Configura índices y prepara la colección"""
    try:
        collection.create_indexes([
            IndexModel([("ubicacion", "2dsphere")], name="geoindex"),
            IndexModel([("tipo", ASCENDING), ("timestamp", ASCENDING)])
        ])
    except OperationFailure as e:
        logging.error(f"Error configurando índices: {str(e)}")

def main():
    client = MongoClient(**MONGO_CONFIG)
    db = client[os.getenv("MONGO_DB", "trafico")]
    collection = db.alertas
    inicializar_mongodb(collection)
    
    intervalo = 45  
    min_intervalo = 20
    max_intervalo = 300
    
    while True:
        try:
            start_time = time.time()
            logging.info(f"Iniciando ciclo de scraping ({GRID_STEPS}x{GRID_STEPS} grids)")
            
            grids = generar_grid()
            alertas_totales = []
            
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(obtener_alertas_grid, grid): grid for grid in grids}
                
                for future in futures:
                    try:
                        alertas = future.result()
                        alertas_totales.extend(alertas)
                    except Exception as e:
                        logging.error(f"Error procesando grid: {str(e)}")
            
            exitosos = 0
            batch_size = 50
            for i in range(0, len(alertas_totales), batch_size):
                batch = alertas_totales[i:i+batch_size]
                exitosos += sum(procesar_alerta(alerta, collection) for alerta in batch)
            
            total = len(alertas_totales)
            ratio_exito = exitosos / total if total > 0 else 0
            
            nuevo_intervalo = intervalo * (1.3 - ratio_exito)
            intervalo = max(min_intervalo, min(max_intervalo, nuevo_intervalo))
            
            tiempo_ejecucion = time.time() - start_time
            logging.info(
                f"Procesadas: {exitosos}/{total} alertas | "
                f"Grids: {len(grids)} | "
                f"Tiempo: {tiempo_ejecucion:.1f}s | "
                f"Próximo ciclo: {intervalo:.1f}s"
            )
            
            sleep_time = max(5, intervalo - tiempo_ejecucion)
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logging.info("\nScraper detenido por el usuario")
            break
        except Exception as e:
            logging.error(f"Error crítico: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    main()