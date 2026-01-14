import time
import random
import sys
from sistema_central import SistemaCentral
from cliente import Cliente

def obtener_entradas():
    print("\n--- CONFIGURACIÓN DE SIMULACIÓN ---")
    try:
        # Solicita parámetros iniciales al usuario
        return int(input("Taxis Automáticos (N): ")), \
               int(input("Clientes (M): ")), \
               int(input("Días a simular: "))
    except ValueError:
        # Valores por defecto si el usuario ingresa algo inválido
        return 5, 5, 1 

def ejecutar_simulacion():
    sistema = SistemaCentral()
    cupo_taxis, num_clientes, num_dias = obtener_entradas()
    
    # --- FASE 1: CONTRATACIÓN (FILTRO) ---
    print(f"\nIniciando selección para {cupo_taxis} vacantes...")
    aceptados, candidato = 0, 1

    # Bucle de contratación: Sigue intentando hasta llenar el cupo (N)
    while aceptados < cupo_taxis:
        # Generación aleatoria de atributos del conductor y vehículo
        datos_cond = {
            'nombre': f"Bot_{candidato}", 
            'antecedentes_penales': random.random() < 0.15, # 15% prob de tener antecedentes
            'licencia_vigente': random.random() > 0.10, 
            'certificado_medico': True
        }
        datos_veh = {
            'modelo': random.choice(['Toyota', 'Ford', 'Chevrolet', 'Nissan']), 
            'placa': f"BOT-{random.randint(100,999)}", 
            'seguro_al_dia': random.random() > 0.05, 
            'impuestos_pagos': True
        }
        
        # El sistema decide si acepta al taxi basándose en reglas
        if sistema.procesar_afiliacion(datos_cond, datos_veh):
            aceptados += 1
        else:
            time.sleep(0.05) # Pequeña pausa si es rechazado
        candidato += 1

    print(f"\nCupo completado. {aceptados} taxis listos.\n" + "-"*60)

    # --- FASE 2: INICIO DE HILOS DE CLIENTES ---
    # Se crean M clientes y se inician como hilos independientes (daemon=True para que mueran al cerrar main)
    clientes = [Cliente(f"C{i+1}", sistema) for i in range(num_clientes)]
    for c in clientes:
        c.daemon = True
        c.start()

    # --- FASE 3: BUCLE DE TIEMPO (DÍAS Y HORAS) ---
    for dia in range(1, num_dias + 1):
        print(f"\n=== INICIO DÍA {dia} ===")
        # Simula horas operativas de 6:00 a 24:00
        for hora in range(6, 25): 
            sistema.actualizar_tiempo(dia, hora)
            print(f"\n--- {hora}:00 H ---")
            time.sleep(1.0) # 1 segundo real = 1 hora simulada

        # Cierre del día
        print("Pausando para cierre del día...")
        time.sleep(1.5) 
        print(f"FIN DEL DÍA {dia}: Recuento...")
        sistema.balance_final_dia() # Imprime tabla diaria y resetea contadores diarios

    # --- FASE 4: FINALIZACIÓN ---
    print("\nDeteniendo flota para Balance Global...")
    # Señal de parada (flag) para que los hilos terminen sus bucles while
    for c in clientes: c.parar = True
    for t in sistema.taxis_registrados: t.parar = True

    print("Finalizando trayectos pendientes...")
    time.sleep(3) # Da tiempo a que los taxis terminen su último viaje

    print("\nSimulación finalizada. Generando Balance Global...")
    sistema.balance_global_simulacion()
    sys.exit()

if __name__ == "__main__":
    ejecutar_simulacion()