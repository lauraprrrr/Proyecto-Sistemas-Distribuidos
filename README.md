# Proyecto-Sistemas-Distribuidos


comandos pa q corra !!!!

docker-compose build    

docker-compose up       


para ver las metricas

python graficar_metricas.py


PRUEBAS
-Poisson + LRU

docker compose down -v
CACHE_POLICY=LRU DISTRIBUTION=poisson docker compose up --build

-Poisson + LFU

docker compose down -v
CACHE_POLICY=LFU DISTRIBUTION=poisson docker compose up --build

-Exponential + LRU

docker compose down -v
CACHE_POLICY=LRU DISTRIBUTION=exponential docker compose up --build

-Exponential + LFU

docker compose down -v
CACHE_POLICY=LFU DISTRIBUTION=exponential docker compose up --build