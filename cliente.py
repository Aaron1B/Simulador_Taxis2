import threading
import time
import random

GRID_SIZE = 25 

class Cliente(threading.Thread):
    def __init__(self, uid, sistema):
        super().__init__()
        self.id = uid
        self.sistema = sistema
        self.parar = False

    def run(self):
        while not self.parar:
            time.sleep(random.uniform(2, 6))
            if self.parar: break

            # Generar coordenadas distintas
            origen = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            destino = origen
            while destino == origen:
                destino = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))

            taxi = self.sistema.match_cliente_taxi(self.id, origen, destino)
            
            # Polling simple de espera
            if taxi:
                while not taxi.esta_libre and taxi.cliente == self.id:
                    time.sleep(0.1)
                # Calificar (ahora solo un número directo)
                self.sistema.recibir_reporte_calidad(self.id, taxi.id, random.randint(3, 5))