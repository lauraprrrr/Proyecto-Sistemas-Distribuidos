import subprocess

services = [
    "almacenamiento",
    "visualizacion",
    "hadoop",      
    "namenode",
    "datanode",
    "elasticsearch",
    "kibana"
]

def run_pipeline():

    if "hadoop" in services:
        services.remove("hadoop")
    cmd = ["docker-compose", "up", "--build"] + services
    subprocess.run(cmd)

if __name__ == "__main__":
    run_pipeline()
