import subprocess

scripts = [
    "/app/scripts/incidentes_por_comuna.pig",
    "/app/scripts/frecuencia_tipos.pig",
    "/app/scripts/tendencias_temporales.pig"
]

output_paths = [
    "/user/proyecto/output/incidentes_por_comuna",
    "/user/proyecto/output/frecuencia_tipos",
    "/user/proyecto/output/tendencias_temporales"
]

local_output_paths = [
    "/app/resultados/incidentes_por_comuna.csv",
    "/app/resultados/frecuencia_tipos.csv",
    "/app/resultados/tendencias_temporales.csv"
]

for script in scripts:
    print(f"Ejecutando script Pig: {script}")
    subprocess.run(["pig", script], check=True)

for hdfs_path, local_path in zip(output_paths, local_output_paths):
    print(f"Copiando desde HDFS: {hdfs_path} a local: {local_path}")
    subprocess.run(["hdfs", "dfs", "-getmerge", hdfs_path, local_path], check=True)

