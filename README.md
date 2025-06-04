# Proyecto-Sistemas-Distribuidos


comandos pa q corra !!!!

docker-compose build    

docker-compose up       


para ver las metricas graficadas

python graficar_metricas.py


PRUEBAS


# Poisson + LRU
DISTRIBUTION=poisson CACHE_POLICY=allkeys-lru docker compose up --build

# Poisson + LFU
DISTRIBUTION=poisson CACHE_POLICY=allkeys-lfu docker compose up --build

# Exponential + LRU
DISTRIBUTION=exponential CACHE_POLICY=allkeys-lru docker compose up --build

# Exponential + LFU
DISTRIBUTION=exponential CACHE_POLICY=allkeys-lfu docker compose up --build




 