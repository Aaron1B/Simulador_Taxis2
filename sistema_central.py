import threading
import time
import random
from taxi import Taxi

GRID_SIZE = 25
RADIO_BUSQUEDA = 8.0 # Distancia máxima para buscar taxi
TASA_SERVICIO = 0.20 # La empresa se queda con el 20%

class SistemaCentral:
    def __init__(self, taxis_iniciales=None):
        self.taxis_registrados = taxis_iniciales if taxis_iniciales else []
        self.viajes_en_curso = {}      
        self.reportes_calidad = []     
        self.dia, self.hora = 1, 6
        
        # --- SEMÁFOROS (CRUCIAL PARA CONCURRENCIA) ---
        # sem_match: Evita que dos hilos (clientes) busquen taxi simultáneamente y elijan el mismo.
        self.sem_match = threading.Semaphore(1) 
        # sem_balance: Evita que se imprima la tabla mientras se actualizan datos.
        self.sem_balance = threading.Semaphore(1)
        print(f"Sistema Central UNIETAXI iniciado. Red: {GRID_SIZE}x{GRID_SIZE}")

    def procesar_afiliacion(self, datos_cond, datos_veh):
        # Lógica booleana para aprobar/rechazar conductores en Fase 1
        if datos_cond['antecedentes_penales'] or \
           not (datos_cond['licencia_vigente'] and datos_cond['certificado_medico']) or \
           not (datos_veh['seguro_al_dia'] and datos_veh['impuestos_pagos']):
            print(f"🔴 SOLICITUD RECHAZADA: {datos_cond['nombre']} no cumple requisitos.")
            return False

        # Si pasa, crea el objeto Taxi (hilo) y lo arranca
        nuevo_id = f"T{len(self.taxis_registrados) + 1}"
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
        # INICIO SECCIÓN CRÍTICA: Solo un cliente entra aquí a la vez
        with self.sem_match:
            if self.hora == 24: # Regla de negocio: Cierre de servicio
                print(f"[{self.get_hora_str()}] 🔴 SOLICITUD DENEGADA {cliente_id}: Cierre 24:00.")
                return None
            
            print(f"[{self.get_hora_str()}] 🟡 Cliente {cliente_id} busca taxi en {origen}...")
            
            # Buscar taxis libres y calcular distancia Euclidiana
            candidatos = []
            for taxi in self.taxis_registrados:
                if taxi.esta_libre:
                    dist = ((taxi.posicion_actual[0] - origen[0])**2 + (taxi.posicion_actual[1] - origen[1])**2)**0.5
                    if dist <= RADIO_BUSQUEDA:
                        candidatos.append((taxi, dist))

            if not candidatos:
                print(f"[{self.get_hora_str()}] 🔴 No hay taxis libres cerca para {cliente_id}.")
                return None
            
            # Ordena candidatos: Primero por cercanía, luego por mejor calificación (desempate)
            candidatos.sort(key=lambda x: (x[1], -x[0].calificacion))
            taxi_asignado, distancia_servicio = candidatos[0]
            
            # Modifica el estado del taxi (ahora está ocupado)
            taxi_asignado.asignar_servicio(cliente_id, origen, destino, distancia_servicio)
            self.viajes_en_curso[cliente_id] = taxi_asignado.id
            
            print(f"[{self.get_hora_str()}] 🔵 Asignado Taxi {taxi_asignado.id} ({taxi_asignado.modelo}).")
            return taxi_asignado
        # FIN SECCIÓN CRÍTICA

    def _imprimir_tabla(self, titulo, es_historico=False):
        # Usa semáforo para evitar que se escriba en consola mezclado con otros prints
        with self.sem_balance:
            print(f"\n--- {titulo} ---")
            ganancia_total = 0
            headers = ["ID", "MODELO", "PLACA", "VIAJES", "BRUTO", "COMISIÓN", "NETO"]
            print(f"{headers[0]:<5} {headers[1]:<10} {headers[2]:<8} {headers[3]:<7} {headers[4]:<9} {headers[5]:<10} {headers[6]:<10}")
            print("-" * 65)
            
            for taxi in self.taxis_registrados:
                # Decide si mostrar datos del día o el acumulado total
                bruto = taxi.saldo_historico if es_historico else taxi.saldo_diario
                viajes = taxi.viajes_historicos if es_historico else taxi.viajes_hoy
                
                comision = bruto * TASA_SERVICIO
                neto = bruto - comision
                ganancia_total += comision
                
                print(f"{taxi.id:<5} {taxi.modelo:<10} {taxi.placa:<8} {viajes:<7} ${bruto:<8.2f} ${comision:<9.2f} ${neto:<9.2f}")
                
                if not es_historico: 
                    taxi.reiniciar_dia() # Resetea contadores para el día siguiente

            print("-" * 65)
            etiqueta = "TOTAL HISTÓRICA" if es_historico else f"(Día {self.dia})"
            print(f"Ganancia UNIETAXI {etiqueta}: ${ganancia_total:.2f}")
            print("=" * 65 + "\n")

    def balance_final_dia(self):
        self._imprimir_tabla(f"RECUENTO FINAL DÍA {self.dia}", es_historico=False)

    def balance_global_simulacion(self):
        self._imprimir_tabla(f"RESUMEN GLOBAL FINAL (TOTAL {self.dia} DÍAS)", es_historico=True)

    def recibir_reporte_calidad(self, cliente_id, taxi_id, calificacion):
        for t in self.taxis_registrados:
            if t.id == taxi_id:
                # Promedio móvil simple para actualizar la calificación del taxi
                t.calificacion = (t.calificacion + calificacion) / 2
                break