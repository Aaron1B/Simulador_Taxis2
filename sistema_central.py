import threading
import time
import random
from taxi import Taxi

GRID_SIZE = 25
RADIO_BUSQUEDA = 8.0
TASA_SERVICIO = 0.20 

class SistemaCentral:
    def __init__(self, taxis_iniciales=None):
        self.taxis_registrados = taxis_iniciales if taxis_iniciales else []
        self.viajes_en_curso = {}      
        self.reportes_calidad = []     
        self.dia, self.hora = 1, 6
        self.sem_match = threading.Semaphore(1)
        self.sem_balance = threading.Semaphore(1)
        print(f"Sistema Central UNIETAXI iniciado. Red: {GRID_SIZE}x{GRID_SIZE}")

    def procesar_afiliacion(self, datos_cond, datos_veh):
        # Validaciones en una sola línea lógica
        if datos_cond['antecedentes_penales'] or \
           not (datos_cond['licencia_vigente'] and datos_cond['certificado_medico']) or \
           not (datos_veh['seguro_al_dia'] and datos_veh['impuestos_pagos']):
            print(f"🔴 SOLICITUD RECHAZADA: {datos_cond['nombre']} no cumple requisitos.")
            return False

        nuevo_id = f"T{len(self.taxis_registrados) + 1}"
        # Generar posición inicial aleatoria
        pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
        
        nuevo_taxi = Taxi(nuevo_id, self, datos_veh['modelo'], datos_veh['placa'], pos)
        nuevo_taxi.daemon = True
        nuevo_taxi.start()
        
        self.taxis_registrados.append(nuevo_taxi)
        print(f"🟢 SOLICITUD APROBADA: {datos_cond['nombre']} afiliado con ID {nuevo_id}.")
        return True

    def actualizar_tiempo(self, dia, hora):
        self.dia, self.hora = dia, hora

    def get_hora_str(self):
        return f"Día {self.dia} - {self.hora}:00"

    def match_cliente_taxi(self, cliente_id, origen, destino):
        with self.sem_match: # Context Manager en lugar de acquire/release manual
            if self.hora == 24:
                print(f"[{self.get_hora_str()}] 🔴 SOLICITUD DENEGADA {cliente_id}: Cierre 24:00.")
                return None
            
            print(f"[{self.get_hora_str()}] 🟡 Cliente {cliente_id} busca taxi en {origen}...")
            
            candidatos = []
            for taxi in self.taxis_registrados:
                if taxi.esta_libre:
                    # Distancia Euclidiana
                    dist = ((taxi.posicion_actual[0] - origen[0])**2 + (taxi.posicion_actual[1] - origen[1])**2)**0.5
                    if dist <= RADIO_BUSQUEDA:
                        candidatos.append((taxi, dist))

            if not candidatos:
                print(f"[{self.get_hora_str()}] 🔴 No hay taxis libres cerca para {cliente_id}.")
                return None
            
            # Ordenar por distancia (menor a mayor) y luego calidad (mayor a menor)
            candidatos.sort(key=lambda x: (x[1], -x[0].calificacion))
            taxi_asignado, distancia_servicio = candidatos[0]
            
            # OPTIMIZACIÓN: Pasamos la distancia calculada para que el taxi no la recalcule
            taxi_asignado.asignar_servicio(cliente_id, origen, destino, distancia_servicio)
            self.viajes_en_curso[cliente_id] = taxi_asignado.id
            
            print(f"[{self.get_hora_str()}] 🔵 Asignado Taxi {taxi_asignado.id} ({taxi_asignado.modelo}).")
            return taxi_asignado

    def _imprimir_tabla(self, titulo, es_historico=False):
        """Función auxiliar para evitar código duplicado en los reportes."""
        with self.sem_balance:
            print(f"\n--- {titulo} ---")
            ganancia_total = 0
            headers = ["ID", "MODELO", "PLACA", "VIAJES", "BRUTO", "COMISIÓN", "NETO"]
            print(f"{headers[0]:<5} {headers[1]:<10} {headers[2]:<8} {headers[3]:<7} {headers[4]:<9} {headers[5]:<10} {headers[6]:<10}")
            print("-" * 65)
            
            for taxi in self.taxis_registrados:
                # Seleccionar origen de datos (Diario vs Histórico)
                bruto = taxi.saldo_historico if es_historico else taxi.saldo_diario
                viajes = taxi.viajes_historicos if es_historico else taxi.viajes_hoy
                
                comision = bruto * TASA_SERVICIO
                neto = bruto - comision
                ganancia_total += comision
                
                print(f"{taxi.id:<5} {taxi.modelo:<10} {taxi.placa:<8} {viajes:<7} ${bruto:<8.2f} ${comision:<9.2f} ${neto:<9.2f}")
                
                # Reiniciar solo si es reporte diario
                if not es_historico: 
                    taxi.reiniciar_dia()

            print("-" * 65)
            etiqueta = "TOTAL HISTÓRICA" if es_historico else f"(Día {self.dia})"
            print(f"Ganancia UNIETAXI {etiqueta}: ${ganancia_total:.2f}")
            print("=" * 65 + "\n")

    def balance_final_dia(self):
        self._imprimir_tabla(f"RECUENTO FINAL DÍA {self.dia}", es_historico=False)

    def balance_global_simulacion(self):
        self._imprimir_tabla(f"RESUMEN GLOBAL FINAL (TOTAL {self.dia} DÍAS)", es_historico=True)

    def recibir_reporte_calidad(self, cliente_id, taxi_id, calificacion):
        # Promedio acumulativo simple
        for t in self.taxis_registrados:
            if t.id == taxi_id:
                t.calificacion = (t.calificacion + calificacion) / 2
                break