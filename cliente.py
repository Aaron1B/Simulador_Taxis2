import threading
import time
import random

GRID_SIZE = 25 

class Cliente(threading.Thread):
    def __init__(self, uid, sistema):
        super().__init__()
        self.id = uid
        self.sistema = sistema
        self.parar = False # Bandera para detener el hilo suavemente

    def run(self):
        while not self.parar:
            # 1. Simula tiempo de espera entre viajes (2 a 6 segs)
            time.sleep(random.uniform(2, 6))
            if self.parar: break

            # 2. Define origen y destino aleatorios en la cuadrícula
            origen = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            destino = origen
            while destino == origen: # Asegura que se mueva a algún lado
                destino = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))

            # 3. Solicita un taxi al sistema central (bloqueante hasta recibir respuesta)
            taxi = self.sistema.match_cliente_taxi(self.id, origen, destino)
            
            if taxi:
                # 4. Si consiguió taxi, ESPERA activa hasta que el taxi termine el viaje.
                # Verifica: que el taxi ya no esté libre y que él sea el cliente asignado.
                while not taxi.esta_libre and taxi.cliente == self.id:
                    time.sleep(0.1) # Polling (comprobación periódica)
                
                # 5. Al terminar, envía calificación al sistema
                self.sistema.recibir_reporte_calidad(self.id, taxi.id, random.randint(3, 5))