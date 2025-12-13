import time
import random
import sys
from sistema_central import SistemaCentral
from cliente import Cliente

def obtener_entradas():
    print("\n--- CONFIGURACIÓN DE SIMULACIÓN ---")
    try:
        # Uso de comprensión de lista para inputs (opcional, pero ahorra espacio visual)
        return int(input("Taxis Automáticos (N): ")), \
               int(input("Clientes (M): ")), \
               int(input("Días a simular: "))
    except ValueError:
        return 5, 5, 1 

def ejecutar_simulacion():
    sistema = SistemaCentral()
    cupo_taxis, num_clientes, num_dias = obtener_entradas()
    
    print(f"\nIniciando selección para {cupo_taxis} vacantes...")
    aceptados, candidato = 0, 1

    while aceptados < cupo_taxis:
        # Generación compacta de datos
        datos_cond = {
            'nombre': f"Bot_{candidato}", 
            'antecedentes_penales': random.random() < 0.15,
            'licencia_vigente': random.random() > 0.10, 
            'certificado_medico': True
        }
        datos_veh = {
            'modelo': random.choice(['Toyota', 'Ford', 'Chevrolet', 'Nissan']), 
            'placa': f"BOT-{random.randint(100,999)}", 
            'seguro_al_dia': random.random() > 0.05, 
            'impuestos_pagos': True
        }
        
        if sistema.procesar_afiliacion(datos_cond, datos_veh):
            aceptados += 1
        else:
            time.sleep(0.05)
        candidato += 1

    print(f"\nCupo completado. {aceptados} taxis listos.\n" + "-"*60)

    # Inicio de Clientes
    clientes = [Cliente(f"C{i+1}", sistema) for i in range(num_clientes)]
    for c in clientes:
        c.daemon = True
        c.start()

    # Bucle Principal
    for dia in range(1, num_dias + 1):
        print(f"\n=== INICIO DÍA {dia} ===")
        for hora in range(6, 25): 
            sistema.actualizar_tiempo(dia, hora)
            print(f"\n--- {hora}:00 H ---")
            time.sleep(1.0) 

        print("Pausando para cierre del día...")
        time.sleep(1.5) 
        print(f"FIN DEL DÍA {dia}: Recuento...")
        sistema.balance_final_dia()

    # Fase de Apagado
    print("\nDeteniendo flota para Balance Global...")
    for c in clientes: c.parar = True
    for t in sistema.taxis_registrados: t.parar = True

    print("Finalizando trayectos pendientes...")
    time.sleep(3) 

    print("\nSimulación finalizada. Generando Balance Global...")
    sistema.balance_global_simulacion()
    sys.exit()

if __name__ == "__main__":
    ejecutar_simulacion()