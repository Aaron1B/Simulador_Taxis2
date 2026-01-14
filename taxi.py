import threading
import time

PRECIO_UNIDAD = 2.50
VELOCIDAD = 20.0 # Velocidad ficticia para calcular tiempo de espera

class Taxi(threading.Thread):
    def __init__(self, uid, sistema, modelo, placa, pos=(0, 0)):
        super().__init__()
        self.id = uid
        self.modelo, self.placa = modelo, placa
        self.sistema = sistema
        self.posicion_actual = pos
        self.calificacion = 5.0
        self.esta_libre = True # Flag crítico: determina disponibilidad
        
        # Datos del viaje actual
        self.cliente = None
        self.destino = None
        self.distancia_servicio = 0.0
        
        # Contabilidad (separada en diaria e histórica)
        self.saldo_diario = 0.0
        self.viajes_hoy = 0 
        self.saldo_historico = 0.0
        self.viajes_historicos = 0
        self.parar = False

    def asignar_servicio(self, cliente_id, origen, destino, distancia):
        # Método llamado por el SistemaCentral
        self.esta_libre = False
        self.cliente = cliente_id
        self.posicion_actual = origen # Se "teletransporta" al origen del cliente
        self.destino = destino
        self.distancia_servicio = distancia

    def reiniciar_dia(self):
        self.saldo_diario = 0.0
        self.viajes_hoy = 0

    def run(self):
        while not self.parar:
            # Si tiene trabajo asignado:
            if not self.esta_libre and self.cliente:
                # 1. Calcular física del viaje
                tiempo_viaje = self.distancia_servicio / VELOCIDAD
                costo = 5.00 + (self.distancia_servicio * PRECIO_UNIDAD) # Tarifa base 5.00

                # 2. Simular conducción (Sleep bloqueante)
                time.sleep(0.5 + tiempo_viaje)
                
                # 3. Llegada a destino
                self.posicion_actual = self.destino
                hora = self.sistema.get_hora_str() if self.sistema else "00:00"
                
                print(f"[{hora}] 🟢 Taxi {self.id} ({self.modelo}-{self.placa}) FINALIZÓ carrera.")
                print(f"   ↳ Distancia: {self.distancia_servicio:.2f} km | Costo: ${costo:.2f}")

                # 4. Actualizar contabilidad
                self.saldo_diario += costo
                self.saldo_historico += costo
                self.viajes_hoy += 1
                self.viajes_historicos += 1
                
                # 5. Liberar taxi para el siguiente cliente
                self.cliente = None
                self.esta_libre = True
            else:
                # Si está libre, duerme un poco para no saturar la CPU
                time.sleep(0.5)