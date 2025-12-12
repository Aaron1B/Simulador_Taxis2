# cliente.py
import threading
import time
import random

# Definimos el tamaño de la red aquí también para generar coordenadas válidas
GRID_SIZE = 25 

class Cliente(threading.Thread):
    def __init__(self, cliente_id, sistema_central):
        super().__init__()
        self.id = cliente_id
        self.sistema_central = sistema_central
        self.parar = False

    def run(self):
        while not self.parar:
            # Espera aleatoria antes de pedir taxi
            time.sleep(random.uniform(2, 6))
            
            if self.parar: break

            # Generar coordenadas dentro de la red 25x25 (0 a 24)
            origen = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            destino = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            
            # Evitar viajes donde origen == destino
            while origen == destino:
                destino = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))

            # Solicitar servicio
            taxi = self.sistema_central.match_cliente_taxi(self.id, origen, destino)
            
            if taxi:
                # Esperar a que el taxi termine (polling simple)
                while not taxi.esta_libre and taxi.cliente_actual == self.id:
                    time.sleep(0.1)
                
                # Calificar
                calificacion = random.randint(3, 5) # Clientes suelen ser generosos
                self.sistema_central.recibir_reporte_calidad(self.id, taxi.id, calificacion)