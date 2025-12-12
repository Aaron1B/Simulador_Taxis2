# main.py
import time
import random
import sys
from sistema_central import SistemaCentral
from taxi import Taxi
from cliente import Cliente

GRID_SIZE = 25

def obtener_entradas():
    print("🚖 --- CONFIGURACIÓN SISTEMA UNIETAXI --- 🚖")
    try:
        n_taxis = int(input("Ingrese número de Taxis (N): "))
        m_clientes = int(input("Ingrese número de Clientes (M): "))
        dias = int(input("Ingrese número de días a simular: "))
        return n_taxis, m_clientes, dias
    except ValueError:
        return 5, 5, 1 

def ejecutar_simulacion():
    num_taxis, num_clientes, num_dias = obtener_entradas()

    # 1. Inicializar Taxis en posiciones aleatorias de la red 25x25
    taxis = []
    for i in range(num_taxis):
        pos_inicial = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
        taxis.append(Taxi(f"T{i+1}", None, pos_inicial))

    sistema = SistemaCentral(taxis)
    
    for t in taxis: t.sistema_central = sistema
    
    clientes = [Cliente(f"C{j+1}", sistema) for j in range(num_clientes)]

    # 2. Iniciar Hilos Daemon
    all_threads = taxis + clientes
    for t in all_threads:
        t.daemon = True
        t.start()

    # 3. Bucle Principal de Tiempo
    for dia in range(1, num_dias + 1):
        print(f"\n📅 === INICIO DÍA {dia} ===")
        
        for hora in range(6, 25): 
            sistema.actualizar_tiempo(dia, hora)
            print(f"\n⌚ --- {hora}:00 H ---")
            
            # Tiempo de simulación por hora
            time.sleep(1.5) 

        # 4. BALANCE FINAL DEL DÍA (Fuera del bucle horario)
        print("⏸️  Pausando actividad para registrar logs finales...")
        time.sleep(1.5) # Dar tiempo a que los taxis terminen sus rutas
        
        print(f"🌙 FIN DEL DÍA {dia}: Realizando recuento y balance...")
        sistema.balance_final_dia()

    print("\n🏁 Fin de la simulación. Cerrando sistema...")
    sys.exit()

if __name__ == "__main__":
    ejecutar_simulacion()