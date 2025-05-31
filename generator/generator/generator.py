import os
import time
import random
import logging
import requests
from pymongo import MongoClient
from scipy.stats import poisson, expon

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class TrafficGenerator:
    def __init__(self):
        self.mongo_client = MongoClient(
            host=os.getenv("MONGO_HOST", "almacenamiento"),
            port=int(os.getenv("MONGO_PORT", 27017)),
            username=os.getenv("MONGO_USER", "root"),
            password=os.getenv("MONGO_PASS", "example"),
            authSource="admin"
        )
        self.db = self.mongo_client.trafico
        self.collection = self.db.alertas
        self.ids = self.collection.distinct("_id")
        if not self.ids:
            raise Exception("No hay IDs en MongoDB")

        self.distribution = os.getenv("DISTRIBUTION", "poisson")
        self.lambda_param = float(os.getenv("LAMBDA", 3.0))
        self.interval = float(os.getenv("INTERVAL", 1.0))
        self.cache_url = os.getenv("CACHE_URL", "http://cache:5000")

    def consultar_api(self, id):
        try:
            res = requests.get(f"{self.cache_url}/evento/{id}", timeout=5)
            if res.status_code == 200:
                data = res.json()
                logging.info(f"[{data['source'].upper()}] ID: {id}")
            else:
                logging.warning(f"ID {id} no encontrado")
        except Exception as e:
            logging.error(f"Error: {e}")

    def poisson_process(self):
        while True:
            rate = poisson.rvs(mu=self.lambda_param)
            for _ in range(rate):
                id = random.choice(self.ids)
                self.consultar_api(id)
            time.sleep(1)

    def exponential_process(self):
        while True:
            id = random.choice(self.ids)
            self.consultar_api(id)
            time.sleep(expon.rvs(scale=self.interval))

    def run(self):
        logging.info(f"Distribución activa: {self.distribution.upper()}")
        if self.distribution == "poisson":
            self.poisson_process()
        else:
            self.exponential_process()

if __name__ == "__main__":
    TrafficGenerator().run()