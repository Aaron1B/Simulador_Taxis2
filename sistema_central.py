# sistema_central.py
import threading
import time
import random

# --- CONSTANTES DE LA SIMULACIÓN ---
GRID_SIZE = 25            # Red de 25x25
RADIO_BUSQUEDA = 8.0      # Radio de cobertura para encontrar taxi
TASA_SERVICIO_UNIETAXI = 0.20 

class SistemaCentral:
    def __init__(self, taxis):
        self.taxis_registrados = taxis 
        self.viajes_en_curso = {}      
        self.reportes_calidad = []     
        
        self.dia_actual = 1
        self.hora_actual = 6

        # Semáforos
        self.semaforo_match = threading.Semaphore(1)
        self.semaforo_balance = threading.Semaphore(1) 

        print(f"🚨 Sistema Central UNIETAXI iniciado. Red: {GRID_SIZE}x{GRID_SIZE}")

    def actualizar_tiempo(self, dia, hora):
        self.dia_actual = dia
        self.hora_actual = hora

    def get_hora_str(self):
        return f"Día {self.dia_actual} - {self.hora_actual}:00"

    # Sección Crítica 1: Match
    def match_cliente_taxi(self, cliente_id, origen, destino):
        self.semaforo_match.acquire()
        try:
            print(f"[{self.get_hora_str()}] 🔍 Cliente {cliente_id} en {origen} busca ir a {destino}...")

            taxis_cercanos = []
            for taxi in self.taxis_registrados:
                # Distancia Euclidiana
                distancia = ((taxi.posicion_actual[0] - origen[0])**2 + (taxi.posicion_actual[1] - origen[1])**2)**0.5
                
                if distancia <= RADIO_BUSQUEDA and taxi.esta_libre:
                    taxis_cercanos.append((taxi, distancia))

            if not taxis_cercanos:
                print(f"[{self.get_hora_str()}] ❌ No hay taxis libres cerca (Radio: {RADIO_BUSQUEDA}u) para {cliente_id}.")
                return None
            
            # Ordenar por cercanía
            taxis_cercanos.sort(key=lambda x: (x[1], -x[0].calificacion_calidad))
            
            taxi_asignado, dist_recogida = taxis_cercanos[0]
            
            # Asignación
            taxi_asignado.asignar_servicio(cliente_id, origen, destino)
            self.viajes_en_curso[cliente_id] = taxi_asignado.id
            
            print(f"[{self.get_hora_str()}] ✅ Asignado Taxi {taxi_asignado.id} (a {dist_recogida:.1f}u de distancia).")
            return taxi_asignado

        finally:
            self.semaforo_match.release()

    # Sección Crítica 2: Balance Final del Día
    def balance_final_dia(self):
        self.semaforo_balance.acquire()
        print(f"\n📊 --- RECUENTO FINAL DÍA {self.dia_actual} ---")

        try:
            ganancia_total = 0
            print(f"{'TAXI ID':<10} {'VIAJES':<8} {'BRUTO':<10} {'COMISIÓN':<12} {'NETO':<12}")
            print("-" * 55)

            for taxi in self.taxis_registrados:
                bruto = taxi.saldo_diario
                comision = bruto * TASA_SERVICIO_UNIETAXI
                neto = bruto - comision
                
                ganancia_total += comision
                
                print(f"{taxi.id:<10} {taxi.viajes_hoy:<8} ${bruto:<9.2f} ${comision:<11.2f} ${neto:<11.2f}")
                
                if hasattr(taxi, 'reiniciar_dia'):
                    taxi.reiniciar_dia()

            print("-" * 55)
            print(f"💰 Ganancia Total UNIETAXI (Día {self.dia_actual}): ${ganancia_total:.2f}")
            print("--------------------------------------------------\n")

        finally:
            self.semaforo_balance.release()

    def recibir_reporte_calidad(self, cliente_id, taxi_id, calificacion):
        self.reportes_calidad.append((cliente_id, taxi_id, calificacion))
        for taxi in self.taxis_registrados:
            if taxi.id == taxi_id:
                taxi.calificacion_calidad = (taxi.calificacion_calidad + calificacion) / 2
                break