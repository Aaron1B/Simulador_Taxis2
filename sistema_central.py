import threading
import time
import random
from taxi import Taxi

# Constantes
GRID_SIZE = 25
RADIO_BUSQUEDA = 8.0
TASA_SERVICIO_UNIETAXI = 0.20 

class SistemaCentral:
    def __init__(self, taxis_iniciales=[]):
        self.taxis_registrados = taxis_iniciales 
        self.viajes_en_curso = {}      
        self.reportes_calidad = []     
        self.dia_actual = 1
        self.hora_actual = 6
        self.semaforo_match = threading.Semaphore(1)
        self.semaforo_balance = threading.Semaphore(1)
        print(f"🚨 Sistema Central UNIETAXI iniciado. Red: {GRID_SIZE}x{GRID_SIZE}")

    # --- NUEVO SISTEMA DE AFILIACIÓN [cite: 32, 46] ---
    def procesar_afiliacion(self, datos_conductor, datos_vehiculo):
        """Valida requisitos y afilia al taxista si cumple condiciones."""
        print(f"\n📄 Procesando solicitud de: {datos_conductor['nombre']}...")
        time.sleep(0.5) # Simula tiempo de revisión

        # 1. Verificación de Antecedentes Penales 
        if datos_conductor['antecedentes_penales']:
            print("❌ SOLICITUD RECHAZADA: El conductor presenta antecedentes penales.")
            return False

        # 2. Verificación de Papeles (Licencia, Médico, Multas) [cite: 48]
        if not datos_conductor['licencia_vigente'] or not datos_conductor['certificado_medico']:
            print("❌ SOLICITUD RECHAZADA: Documentación del conductor vencida o incompleta.")
            return False

        # 3. Verificación del Vehículo (Seguro, Impuestos) [cite: 49]
        if not datos_vehiculo['seguro_al_dia'] or not datos_vehiculo['impuestos_pagos']:
            print("❌ SOLICITUD RECHAZADA: Vehículo insolvente o sin seguro.")
            return False

        # Si pasa todo, se crea el Taxi
        nuevo_id = f"T{len(self.taxis_registrados) + 1}"
        pos_inicial = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
        
        nuevo_taxi = Taxi(
            taxi_id=nuevo_id,
            sistema_central=self,
            modelo=datos_vehiculo['modelo'],
            placa=datos_vehiculo['placa'],
            posicion_inicial=pos_inicial
        )
        
        # Iniciar el hilo del nuevo taxi inmediatamente (Modo Daemon)
        nuevo_taxi.daemon = True
        nuevo_taxi.start()
        
        # Añadir a la lista protegida (en ejecución real debería llevar semáforo, aquí simplificado)
        self.taxis_registrados.append(nuevo_taxi)
        print(f"✅ SOLICITUD APROBADA: {datos_conductor['nombre']} afiliado con ID {nuevo_id}.")
        return True
    # --------------------------------------------------

    def actualizar_tiempo(self, dia, hora):
        self.dia_actual = dia
        self.hora_actual = hora

    def get_hora_str(self):
        return f"Día {self.dia_actual} - {self.hora_actual}:00"

    def match_cliente_taxi(self, cliente_id, origen, destino):
        self.semaforo_match.acquire()
        try:
            print(f"[{self.get_hora_str()}] 🔍 Cliente {cliente_id} busca taxi en {origen}...")
            taxis_cercanos = []
            for taxi in self.taxis_registrados:
                distancia = ((taxi.posicion_actual[0] - origen[0])**2 + (taxi.posicion_actual[1] - origen[1])**2)**0.5
                if distancia <= RADIO_BUSQUEDA and taxi.esta_libre:
                    taxis_cercanos.append((taxi, distancia))

            if not taxis_cercanos:
                print(f"[{self.get_hora_str()}] ❌ No hay taxis libres cerca para {cliente_id}.")
                return None
            
            taxis_cercanos.sort(key=lambda x: (x[1], -x[0].calificacion_calidad))
            taxi_asignado = taxis_cercanos[0][0]
            
            taxi_asignado.asignar_servicio(cliente_id, origen, destino)
            self.viajes_en_curso[cliente_id] = taxi_asignado.id
            print(f"[{self.get_hora_str()}] ✅ Asignado Taxi {taxi_asignado.id} ({taxi_asignado.modelo}).")
            return taxi_asignado
        finally:
            self.semaforo_match.release()

    def balance_final_dia(self):
        self.semaforo_balance.acquire()
        print(f"\n📊 --- RECUENTO FINAL DÍA {self.dia_actual} ---")
        try:
            ganancia_total = 0
            print(f"{'ID':<5} {'MODELO':<10} {'PLACA':<8} {'VIAJES':<7} {'BRUTO':<9} {'COMISIÓN':<10} {'NETO':<10}")
            print("-" * 65)
            for taxi in self.taxis_registrados:
                bruto = taxi.saldo_diario
                comision = bruto * TASA_SERVICIO_UNIETAXI
                neto = bruto - comision
                ganancia_total += comision
                print(f"{taxi.id:<5} {taxi.modelo:<10} {taxi.placa:<8} {taxi.viajes_hoy:<7} ${bruto:<8.2f} ${comision:<9.2f} ${neto:<9.2f}")
                if hasattr(taxi, 'reiniciar_dia'): taxi.reiniciar_dia()

            print("-" * 65)
            print(f"💰 Ganancia Total UNIETAXI (Día {self.dia_actual}): ${ganancia_total:.2f}")
            print("------------------------------------------------------------\n")
        finally:
            self.semaforo_balance.release()

    def recibir_reporte_calidad(self, cliente_id, taxi_id, calificacion):
        self.reportes_calidad.append((cliente_id, taxi_id, calificacion))
        for taxi in self.taxis_registrados:
            if taxi.id == taxi_id:
                taxi.calificacion_calidad = (taxi.calificacion_calidad + calificacion) / 2
                break