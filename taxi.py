# taxi.py
import threading
import time
import random

class Taxi(threading.Thread):
    def __init__(self, taxi_id, sistema_central, posicion_inicial=(0, 0), calificacion=4.0):
        super().__init__()
        self.id = taxi_id
        self.sistema_central = sistema_central
        self.posicion_actual = posicion_inicial
        self.calificacion_calidad = calificacion
        self.esta_libre = True
        self.cliente_actual = None
        self.destino_servicio = None
        self.saldo_diario = 0.0
        self.parar = False

    def asignar_servicio(self, cliente_id, destino):
        self.esta_libre = False
        self.cliente_actual = cliente_id
        self.destino_servicio = destino

    def reiniciar_dia(self):
        """Resetea el saldo al finalizar el cierre contable."""
        self.saldo_diario = 0.0

    def simular_viaje(self):
        if self.cliente_actual is None: return

        # Simulamos tiempo de viaje
        time.sleep(random.uniform(0.5, 1.5))
        
        # Cálculo de costo
        costo_viaje = random.uniform(5.0, 15.0)
        self.saldo_diario += costo_viaje
        
        # Fin del viaje
        self.posicion_actual = self.destino_servicio
        
        # El taxi vuelve a estar libre
        self.destino_servicio = None
        self.cliente_actual = None
        self.esta_libre = True

    def run(self):
        while not self.parar:
            if not self.esta_libre:
                self.simular_viaje()
            else:
                # El taxi se mueve aleatoriamente mientras espera (opcional)
                time.sleep(1)