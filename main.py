import time
import random
import sys
from sistema_central import SistemaCentral
from cliente import Cliente
from taxi import Taxi 

GRID_SIZE = 25

def menu_afiliacion(sistema):
    # (El menú manual se mantiene igual, lo omito para ahorrar espacio)
    # ... Si copias el archivo completo, asegúrate de mantener esta función ...
    while True:
        print("\n🗂️ --- OFICINA DE AFILIACIÓN UNIETAXI ---")
        opcion = input("¿Desea afiliar un nuevo taxi manualmente? (s/n): ").lower()
        if opcion != 's': break
        
        # ... (Lógica de input manual anterior) ...
        # Para el ejemplo completo, mantén el código que te di en la respuesta anterior
        break

def obtener_entradas():
    print("\n🚖 --- CONFIGURACIÓN DE SIMULACIÓN --- 🚖")
    try:
        n_taxis = int(input("Cupo de Taxis Automáticos (N): "))
        m_clientes = int(input("Clientes (M): "))
        dias = int(input("Días a simular: "))
        return n_taxis, m_clientes, dias
    except ValueError:
        return 5, 5, 1 

def ejecutar_simulacion():
    # 1. Crear Sistema Central vacío
    sistema = SistemaCentral(taxis_iniciales=[])

    # 2. Fase de Afiliación Manual (Opcional)
    # menu_afiliacion(sistema) # Descomentar si quieres usarlo

    # 3. Configuración y Generación Automática con RECHAZOS
    cupo_taxis, num_clientes, num_dias = obtener_entradas()
    
    print(f"\n⚙️ Iniciando proceso de selección para {cupo_taxis} vacantes de taxis...")
    
    taxis_aceptados = 0
    candidato_n = 1

    # Intentamos generar candidatos hasta llenar el cupo
    while taxis_aceptados < cupo_taxis:
        
        # --- GENERACIÓN DE DATOS CON PROBABILIDAD DE FALLO ---
        # 15% de probabilidad de tener antecedentes penales
        tiene_antecedentes = random.random() < 0.15
        
        # 10% de probabilidad de tener licencia vencida
        licencia_ok = random.random() > 0.10
        
        # 5% de probabilidad de tener el seguro vencido
        seguro_ok = random.random() > 0.05

        conductor = {
            'nombre': f"Bot_Candidato_{candidato_n}", 
            'antecedentes_penales': tiene_antecedentes, 
            'licencia_vigente': licencia_ok, 
            'certificado_medico': True
        }
        
        vehiculo = {
            'modelo': random.choice(['Toyota', 'Ford', 'Chevrolet', 'Nissan']), 
            'placa': f"BOT-{random.randint(100,999)}", 
            'seguro_al_dia': seguro_ok, 
            'impuestos_pagos': True
        }
        
        # Intentamos afiliar
        exito = sistema.procesar_afiliacion(conductor, vehiculo)
        
        if exito:
            taxis_aceptados += 1
        else:
            print(f"   ⚠️ El candidato Bot_{candidato_n} fue descartado. Buscando otro...")
            time.sleep(0.2) # Pausa dramática pequeña
            
        candidato_n += 1

    print(f"\n✅ Cupo completado. {taxis_aceptados} taxis listos para trabajar.")
    print("------------------------------------------------------------")

    # 4. Iniciar Clientes
    clientes = [Cliente(f"C{j+1}", sistema) for j in range(num_clientes)]
    for c in clientes:
        c.daemon = True
        c.start()

    # 5. Bucle Principal (Igual que antes)
    for dia in range(1, num_dias + 1):
        print(f"\n📅 === INICIO DÍA {dia} ===")
        for hora in range(6, 25): 
            sistema.actualizar_tiempo(dia, hora)
            print(f"\n⌚ --- {hora}:00 H ---")
            time.sleep(1.0) 

        print("⏸️  Pausando actividad para registrar logs finales...")
        time.sleep(1.0) 
        
        print(f"🌙 FIN DEL DÍA {dia}: Realizando recuento y balance...")
        sistema.balance_final_dia()

    print("\n🏁 Fin de la simulación. Cerrando sistema...")
    sys.exit()

if __name__ == "__main__":
    ejecutar_simulacion()