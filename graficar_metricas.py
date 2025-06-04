import requests
import matplotlib.pyplot as plt
import time

URL = "http://localhost:5000/metrics"
intervalo = 60 
duracion_total = 3600  # 1 hora
n_muestras = duracion_total // intervalo

hits = []
misses = []
hit_rates = []
tamanos_cache = []
instantes = []

for i in range(n_muestras):
    try:
        res = requests.get(URL)
        data = res.json()

        hits.append(data["hits"])
        misses.append(data["misses"])
        hit_rates.append(data["hit_rate_decimal"]) 
        tamanos_cache.append(data["cache_size"])
        instantes.append(i * intervalo)

        print(f"{i+1}/{n_muestras} | Hit Rate: {data['hit_rate_percent']} | Hits: {data['hits']} | Misses: {data['misses']}")

    except Exception as e:
        print(f"Error en muestra {i+1}: {e}")

    time.sleep(intervalo)

plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(instantes, hits, label="Hits", color="green")
plt.plot(instantes, misses, label="Misses", color="red")
plt.ylabel("Cantidad")
plt.title("Hits y Misses del Cache")
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(instantes, hit_rates, label="Tasa de aciertos", color="blue")
plt.plot(instantes, tamanos_cache, label="Tamaño del Cache", color="purple")
plt.xlabel("Tiempo (s)")
plt.ylabel("Valor")
plt.title("Tasa de Aciertos (%) y Tamaño del Cache")
plt.legend()

plt.tight_layout()
plt.savefig("metricas_cache_1h.png")
plt.show()
