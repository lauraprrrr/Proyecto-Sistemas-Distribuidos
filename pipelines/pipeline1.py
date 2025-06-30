import subprocess

services = [
    "scraper",
    "almacenamiento",
    "generator",
    "redis",
    "cache"
]

def run_pipeline():
    cmd = ["docker-compose", "up", "--build"] + services
    subprocess.run(cmd)

if __name__ == "__main__":
    run_pipeline()
