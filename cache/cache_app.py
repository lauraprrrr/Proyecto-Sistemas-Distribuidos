from flask import Flask, jsonify
from pymongo import MongoClient
import redis
import json
import os
import logging
from datetime import datetime, timedelta

start_time = datetime.utcnow()
app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # segundos

MONGO_HOST = os.getenv("MONGO_HOST", "almacenamiento")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASS = os.getenv("MONGO_PASS", "example")

# Conexiones
mongo_client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER,
    password=MONGO_PASS,
    authSource="admin"
)
mongo_collection = mongo_client.trafico.alertas

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

hit_count = 0
miss_count = 0

def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(elem) for elem in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

@app.route("/evento/<id>", methods=["GET"])
def get_evento(id):
    global hit_count, miss_count

    # Intentar obtener desde Redis
    cached = redis_client.get(id)
    if cached:
        hit_count += 1
        logging.info(f"✅ HIT ({hit_count}) - ID: {id}")
        return jsonify({"source": "cache", "evento": json.loads(cached)})

    # Si no está en Redis, consultar MongoDB
    doc = mongo_collection.find_one({"_id": id})
    if not doc:
        return jsonify({"error": "No encontrado"}), 404

    miss_count += 1
    logging.info(f"❌ MISS ({miss_count}) - ID: {id}")

    # Guardar en Redis
    redis_client.setex(id, CACHE_TTL, json.dumps(convert_datetime(doc)))

    return jsonify({"source": "mongo", "evento": doc})

@app.route("/metrics")
def metrics():
    try:
        total = hit_count + miss_count
        elapsed = datetime.utcnow() - start_time
        elapsed_str = str(timedelta(seconds=int(elapsed.total_seconds())))
        hit_rate_decimal = round(hit_count / total, 5) if total > 0 else 0
        hit_rate_percent = round(100 * hit_rate_decimal, 2)

        return jsonify({
            "hits": hit_count,
            "misses": miss_count,
            "hit_rate_decimal": hit_rate_decimal,
            "hit_rate_percent": f"{hit_rate_percent}%",
            "cache_size": redis_client.dbsize(),
            "cache_policy": f"Redis {os.getenv('POLITICA_CACHE')} TTL {CACHE_TTL}s",
            "total_requests": total,
            "uptime": elapsed_str
        })
    except Exception as e:
        logging.exception("❌ Error en /metrics:")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.info(f"Ejecutando cache con Redis en {REDIS_HOST}:{REDIS_PORT}, TTL={CACHE_TTL}s")
    app.run(host="0.0.0.0", port=5000)