import threading
import time
import random

GRID_SIZE = 25 

class Cliente(threading.Thread):
    def __init__(self, cliente_id, sistema_central):
        super().__init__()
        self.id = cliente_id
        self.sistema_central = sistema_central
        self.parar = False

    def run(self):
        while not self.parar:
            time.sleep(random.uniform(2, 6)) # Espera aleatoria antes de pedir
            if self.parar: break

            origen = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)) # Coordenadas 0-24
            destino = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            while origen == destino: destino = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)) # Evitar mismo sitio

            taxi = self.sistema_central.match_cliente_taxi(self.id, origen, destino) # Solicitar servicio
            
            if taxi:
                while not taxi.esta_libre and taxi.cliente_actual == self.id: time.sleep(0.1) # Esperar fin del viaje
                calificacion = random.randint(3, 5) 
                self.sistema_central.recibir_reporte_calidad(self.id, taxi.id, calificacion)