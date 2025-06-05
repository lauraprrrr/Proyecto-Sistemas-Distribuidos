# Proyecto-Sistemas-Distribuidos

Este proyecto corresponde a la segunda entrega del curso de Sistemas Distribuidos. Su objetivo es procesar de manera distribuida los eventos de tráfico recolectados desde Waze, utilizando herramientas como HDFS y Apache Pig.


## Cómo ejecutar el proyecto

Construir los contenedores:

```bash
docker-compose build
docker-compose up       
```



# Comandos útiles:

## Para ver graficas de cache

```bash
python graficar_metricas.py     
```

## Pruebas de cache y generador

# Poisson + LRU
DISTRIBUTION=poisson CACHE_POLICY=allkeys-lru docker compose up --build

# Poisson + LFU
DISTRIBUTION=poisson CACHE_POLICY=allkeys-lfu docker compose up --build

# Exponential + LRU
DISTRIBUTION=exponential CACHE_POLICY=allkeys-lru docker compose up --build

# Exponential + LFU
DISTRIBUTION=exponential CACHE_POLICY=allkeys-lfu docker compose up --build


# # Ejecutar scrips Pig


# Entrar a la consola de procesamiento:

```bash
docker exec -it procesamiento bash

pig /scripts/incidentes_por_comuna.pig
pig /scripts/frecuencia_tipos.pig
pig /scripts/tendencias_temporales.pig   

```

