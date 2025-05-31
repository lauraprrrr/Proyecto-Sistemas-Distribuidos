from flask import Flask, jsonify
from pymongo import MongoClient
import os
from collections import OrderedDict, defaultdict
import logging
from datetime import datetime, timedelta

start_time = datetime.utcnow()

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

CACHE_SIZE = int(os.getenv("CACHE_SIZE", 1000))
POLITICA = os.getenv("POLITICA_CACHE", "LRU").upper()

hit_count = 0
miss_count = 0

client = MongoClient(
    host=os.getenv("MONGO_HOST", "almacenamiento"),
    port=int(os.getenv("MONGO_PORT", 27017)),
    username=os.getenv("MONGO_USER", "root"),
    password=os.getenv("MONGO_PASS", "example"),
    authSource="admin"
)
collection = client.trafico.alertas

if POLITICA == "LFU":
    cache = {}
    frecuencias = defaultdict(int)
else:  
    cache = OrderedDict()

@app.route("/evento/<id>", methods=["GET"])
def get_evento(id):
    global cache, hit_count, miss_count

    if id in cache:
        hit_count += 1
        logging.info(f"✅ HIT ({hit_count}) - ID: {id}")

        if POLITICA == "LFU":
            frecuencias[id] += 1
        else:
            cache.move_to_end(id)

        return jsonify({"source": "cache", "evento": cache[id]})

    # Búsqueda en MongoDB
    doc = collection.find_one({"_id": id})

    if not doc:
        return jsonify({"error": "No encontrado"}), 404

    miss_count += 1
    logging.info(f"❌ MISS ({miss_count}) - ID: {id}")

    if len(cache) >= CACHE_SIZE:
        if POLITICA == "LFU":
            menos_usado = min(frecuencias, key=frecuencias.get)
            del cache[menos_usado]
            del frecuencias[menos_usado]
        else:
            cache.popitem(last=False)

    cache[id] = doc
    if POLITICA == "LFU":
        frecuencias[id] = 1

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
            "hits": int(hit_count),
            "misses": int(miss_count),
            "hit_rate_decimal": hit_rate_decimal,
            "hit_rate_percent": f"{hit_rate_percent}%",
            "cache_size": len(cache),
            "cache_policy": POLITICA,
            "total_requests": total,
            "uptime": elapsed_str
        })
    except Exception as e:
        logging.exception("❌ Error en /metrics:")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logging.info(f"Ejecutando cache con política: {POLITICA}")
    app.run(host="0.0.0.0", port=5000)