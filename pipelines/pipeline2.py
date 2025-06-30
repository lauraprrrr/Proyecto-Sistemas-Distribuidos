import subprocess

services = [
    "almacenamiento",
    "filtrado",
    "procesamiento",
    "namenode",
    "datanode"
]

def run_pipeline():
    cmd = ["docker-compose", "up", "--build"] + services
    subprocess.run(cmd)

if __name__ == "__main__":
    run_pipeline()
