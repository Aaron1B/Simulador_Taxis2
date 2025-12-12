# taxi.py
import threading
import time
import random

PRECIO_POR_UNIDAD = 2.50   # Precio por "cuadra" o unidad de distancia
VELOCIDAD_TAXI = 20.0      # Unidades por segundo (simulado para que no tarde demasiado)

class Taxi(threading.Thread):
    def __init__(self, taxi_id, sistema_central, posicion_inicial=(0, 0)):
        super().__init__()
        self.id = taxi_id
        self.sistema_central = sistema_central
        self.posicion_actual = posicion_inicial
        self.calificacion_calidad = 5.0
        
        self.esta_libre = True
        self.cliente_actual = None
        self.origen_servicio = None
        self.destino_servicio = None
        
        self.saldo_diario = 0.0
        self.viajes_hoy = 0 # Contador de viajes
        self.parar = False

    def asignar_servicio(self, cliente_id, origen, destino):
        self.esta_libre = False
        self.cliente_actual = cliente_id
        self.origen_servicio = origen
        self.destino_servicio = destino

    def reiniciar_dia(self):
        self.saldo_diario = 0.0
        self.viajes_hoy = 0

    def simular_viaje(self):
        if self.cliente_actual is None: return

        # 1. Calcular distancia del viaje (Euclidiana)
        dx = self.destino_servicio[0] - self.origen_servicio[0]
        dy = self.destino_servicio[1] - self.origen_servicio[1]
        distancia_viaje = (dx**2 + dy**2)**0.5

        # 2. Calcular tiempo de viaje y costo
        # Tiempo simulado: Si la distancia es 20 y velocidad es 20, duerme 1 seg real.
        tiempo_viaje = distancia_viaje / VELOCIDAD_TAXI
        
        # Costo base (5.00) + Costo por distancia
        costo_total = 5.00 + (distancia_viaje * PRECIO_POR_UNIDAD)

        # 3. Simular el traslado (Sleep)
        # Nota: Añadimos un pequeño delay base para recoger al pasajero
        time.sleep(0.2 + tiempo_viaje)

        # 4. Actualizar estado
        self.saldo_diario += costo_total
        self.viajes_hoy += 1
        self.posicion_actual = self.destino_servicio # El taxi queda en el destino
        
        # Resetear variables de servicio
        self.destino_servicio = None
        self.origen_servicio = None
        self.cliente_actual = None
        self.esta_libre = True

    def run(self):
        while not self.parar:
            if not self.esta_libre:
                self.simular_viaje()
            else:
                time.sleep(0.5)