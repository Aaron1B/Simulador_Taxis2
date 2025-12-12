import threading
import time
import random

# Constantes del sistema
RADIO_BUSQUEDA_KM = 2.0
TASA_SERVICIO_UNIETAXI = 0.20  # 20% de descuento por servicio

class SistemaCentral:
    def __init__(self, taxis):
        # Recursos Críticos
        self.taxis_registrados = taxis  # Lista de objetos Taxi
        self.viajes_en_curso = {}      # {cliente_id: taxi_id}
        self.reportes_calidad = []     # Lista para reportes de calidad
        
        # Variables de tiempo simulado (NUEVO)
        self.dia_actual = 1
        self.hora_actual = 6

        # Primitivas de Sincronización
        self.semaforo_match = threading.Semaphore(1)
        self.semaforo_cierre_contable = threading.Semaphore(1)

        print("🚨 Sistema Central UNIETAXI iniciado.")

    # --- MÉTODO QUE FALTABA ---
    def actualizar_tiempo(self, dia, hora):
        """Actualiza el reloj interno para los logs."""
        self.dia_actual = dia
        self.hora_actual = hora

    def get_hora_str(self):
        """Devuelve la hora formateada para los logs."""
        sufijo = "AM" if self.hora_actual < 12 else "PM"
        return f"Día {self.dia_actual} - {self.hora_actual}:00 {sufijo}"
    # ---------------------------

    # Sección Crítica 1: Asignación de pareja cliente-taxi (Match)
    def match_cliente_taxi(self, cliente_id, origen, destino):
        """Busca y asigna el taxi más cercano al cliente, protegiendo la lista de taxis."""
        
        self.semaforo_match.acquire()
        try:
            # Usamos get_hora_str() para que el log tenga sentido temporal
            print(f"[{self.get_hora_str()}] 🔍 Cliente {cliente_id} busca taxi...")

            taxis_cercanos = []
            
            for taxi in self.taxis_registrados:
                distancia = ((taxi.posicion_actual[0] - origen[0])**2 + (taxi.posicion_actual[1] - origen[1])**2)**0.5
                
                if distancia <= RADIO_BUSQUEDA_KM and taxi.esta_libre:
                    taxis_cercanos.append((taxi, distancia))

            if not taxis_cercanos:
                print(f"[{self.get_hora_str()}] ❌ No hay taxis libres cerca del cliente {cliente_id}.")
                return None
            
            # Ordenar por distancia y desempate por calificación
            taxis_cercanos.sort(key=lambda x: (x[1], -x[0].calificacion_calidad))

            taxi_asignado = taxis_cercanos[0][0]
            
            # Asignación
            taxi_asignado.asignar_servicio(cliente_id, destino)
            self.viajes_en_curso[cliente_id] = taxi_asignado.id
            
            print(f"[{self.get_hora_str()}] ✅ Asignado Taxi {taxi_asignado.id} a Cliente {cliente_id}.")
            return taxi_asignado

        finally:
            self.semaforo_match.release()


    # Sección Crítica 2: Cierre Contable Diario
    def cierre_contable_diario(self):
        """Realiza el cierre contable del día."""
        
        self.semaforo_cierre_contable.acquire()
        print(f"\n🔔 --- [{self.get_hora_str()}] INICIANDO CIERRE CONTABLE ---")

        try:
            ganancia_total = 0
            print(f"{'TAXI ID':<10} {'BRUTO':<10} {'COMISIÓN (20%)':<15} {'NETO TAXISTA':<15}")
            print("-" * 55)

            for taxi in self.taxis_registrados:
                bruto = taxi.saldo_diario
                comision = bruto * TASA_SERVICIO_UNIETAXI
                neto = bruto - comision
                
                ganancia_total += comision
                
                print(f"{taxi.id:<10} ${bruto:<9.2f} ${comision:<14.2f} ${neto:<14.2f}")
                
                # Reiniciar saldo usando el método del taxi
                if hasattr(taxi, 'reiniciar_dia'):
                    taxi.reiniciar_dia()
                else:
                    taxi.saldo_diario = 0

            print("-" * 55)
            print(f"💰 Ganancia Total UNIETAXI (Día {self.dia_actual}): ${ganancia_total:.2f}")
            print("------------------------------------------------------\n")

        finally:
            self.semaforo_cierre_contable.release()

    def recibir_reporte_calidad(self, cliente_id, taxi_id, calificacion):
        """Recibe y almacena un reporte de calidad."""
        self.reportes_calidad.append((cliente_id, taxi_id, calificacion))
        
        for taxi in self.taxis_registrados:
            if taxi.id == taxi_id:
                # Actualizar promedio (simplificado)
                taxi.calificacion_calidad = (taxi.calificacion_calidad + calificacion) / 2
                break

    def seguimiento_aleatorio(self):
        """Simula el seguimiento aleatorio."""
        # Se puede llamar al final del día si se desea
        pass