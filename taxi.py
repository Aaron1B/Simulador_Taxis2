import threading
import time
import random

PRECIO_POR_UNIDAD = 2.50
VELOCIDAD_TAXI = 20.0

class Taxi(threading.Thread):
    # Actualizado con datos de afiliación 
    def __init__(self, taxi_id, sistema_central, modelo, placa, posicion_inicial=(0, 0)):
        super().__init__()
        self.id = taxi_id
        self.modelo = modelo # Nuevo: Marca/Modelo
        self.placa = placa   # Nuevo: Placa
        self.sistema_central = sistema_central
        self.posicion_actual = posicion_inicial
        self.calificacion_calidad = 5.0
        self.esta_libre = True
        self.cliente_actual = None
        self.origen_servicio = None
        self.destino_servicio = None
        self.saldo_diario = 0.0
        self.viajes_hoy = 0 
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
        
        dx = self.destino_servicio[0] - self.origen_servicio[0]
        dy = self.destino_servicio[1] - self.origen_servicio[1]
        distancia_viaje = (dx**2 + dy**2)**0.5
        
        tiempo_viaje = distancia_viaje / VELOCIDAD_TAXI
        costo_total = 5.00 + (distancia_viaje * PRECIO_POR_UNIDAD)

        time.sleep(0.5 + tiempo_viaje)
        self.posicion_actual = self.destino_servicio

        hora_log = "00:00"
        if self.sistema_central: hora_log = self.sistema_central.get_hora_str()

        # Log con detalles del vehículo 
        print(f"[{hora_log}] 🏁 Taxi {self.id} ({self.modelo}-{self.placa}) FINALIZÓ carrera.")
        print(f"   ↳ 📏 Distancia: {distancia_viaje:.2f} km | 💵 Costo: ${costo_total:.2f}")

        self.saldo_diario += costo_total
        self.viajes_hoy += 1
        self.destino_servicio = None; self.origen_servicio = None; self.cliente_actual = None
        self.esta_libre = True

    def run(self):
        while not self.parar:
            if not self.esta_libre:
                self.simular_viaje()
            else:
                time.sleep(0.5)