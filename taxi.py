import threading
import time

PRECIO_UNIDAD = 2.50
VELOCIDAD = 20.0

class Taxi(threading.Thread):
    def __init__(self, uid, sistema, modelo, placa, pos=(0, 0)):
        super().__init__()
        self.id = uid
        self.modelo, self.placa = modelo, placa
        self.sistema = sistema
        self.posicion_actual = pos
        self.calificacion = 5.0
        self.esta_libre = True
        
        # Datos del servicio actual
        self.cliente = None
        self.destino = None
        self.distancia_servicio = 0.0 # Nueva variable para optimización
        
        # Contadores
        self.saldo_diario = 0.0
        self.viajes_hoy = 0 
        self.saldo_historico = 0.0
        self.viajes_historicos = 0
        self.parar = False

    def asignar_servicio(self, cliente_id, origen, destino, distancia):
        self.esta_libre = False
        self.cliente = cliente_id
        self.posicion_actual = origen # Asumimos teletransporte al origen o trayecto incluido
        self.destino = destino
        self.distancia_servicio = distancia # Recibimos el dato pre-calculado

    def reiniciar_dia(self):
        self.saldo_diario = 0.0
        self.viajes_hoy = 0

    def run(self):
        while not self.parar:
            if not self.esta_libre and self.cliente:
                # Lógica de viaje
                tiempo_viaje = self.distancia_servicio / VELOCIDAD
                costo = 5.00 + (self.distancia_servicio * PRECIO_UNIDAD)

                time.sleep(0.5 + tiempo_viaje) # Simulación tiempo
                
                # Finalización
                self.posicion_actual = self.destino
                hora = self.sistema.get_hora_str() if self.sistema else "00:00"
                
                print(f"[{hora}] 🟢 Taxi {self.id} ({self.modelo}-{self.placa}) FINALIZÓ carrera.")
                print(f"   ↳ Distancia: {self.distancia_servicio:.2f} km | Costo: ${costo:.2f}")

                # Actualización de saldos
                self.saldo_diario += costo
                self.saldo_historico += costo
                self.viajes_hoy += 1
                self.viajes_historicos += 1
                
                # Liberar taxi
                self.cliente = None
                self.esta_libre = True
            else:
                time.sleep(0.5)