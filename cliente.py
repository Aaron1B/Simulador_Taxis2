# cliente.py
import threading
import time
import random

class Cliente(threading.Thread):
    def __init__(self, cliente_id, sistema_central):
        super().__init__()
        self.id = cliente_id
        self.sistema_central = sistema_central
        self.parar = False

    def run(self):
        while not self.parar:
            # El cliente espera un tiempo aleatorio antes de pedir un taxi
            # para no saturar la consola instantáneamente
            time.sleep(random.uniform(2, 5))
            
            if self.parar: break

            # [cite_start]Definir origen y destino (coordenadas 0-10) [cite: 37]
            origen = (random.randint(0, 10), random.randint(0, 10))
            destino = (random.randint(0, 10), random.randint(0, 10))
            
            # Solicitar servicio
            taxi = self.sistema_central.match_cliente_taxi(self.id, origen, destino)
            
            if taxi:
                # Esperar a que el taxi termine el viaje (simulado)
                while not taxi.esta_libre and taxi.cliente_actual == self.id:
                    time.sleep(0.1)
                
                # [cite_start]Calificar servicio [cite: 20]
                calificacion = random.randint(1, 5)
                self.sistema_central.recibir_reporte_calidad(self.id, taxi.id, calificacion)