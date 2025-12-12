# main.py
import time
import random
from sistema_central import SistemaCentral
from taxi import Taxi
from cliente import Cliente

def obtener_entradas():
    """Solicita los parámetros de simulación al usuario."""
    print("🚖 --- CONFIGURACIÓN SISTEMA UNIETAXI --- 🚖")
    try:
        n_taxis = int(input("Ingrese número de Taxis (N): "))
        m_clientes = int(input("Ingrese número de Clientes (M): "))
        dias = int(input("Ingrese número de días a simular: "))
        return n_taxis, m_clientes, dias
    except ValueError:
        print("❌ Error: Ingrese solo números enteros.")
        return 5, 5, 1 # Valores por defecto

def ejecutar_simulacion():
    num_taxis, num_clientes, num_dias = obtener_entradas()

    # 1. Inicializar Entidades
    taxis = [Taxi(f"T{i+1}", None, (random.randint(0,10), random.randint(0,10))) for i in range(num_taxis)]
    sistema = SistemaCentral(taxis)
    
    # Vincular sistema a taxis
    for t in taxis: t.sistema_central = sistema
    
    clientes = [Cliente(f"C{j+1}", sistema) for j in range(num_clientes)]

    # 2. Iniciar Hilos (Taxis y Clientes quedan 'vivos' esperando órdenes o eventos)
    print("\n🔥 Iniciando motores (hilos)...")
    for t in taxis: t.start()
    for c in clientes: c.start()

    # 3. Bucle Principal de Tiempo (Días y Horas)
    for dia in range(1, num_dias + 1):
        print(f"\n📅 === INICIO DÍA {dia} ===")
        
        # Simulamos desde las 6 AM hasta las 12 PM (mediodía)
        for hora in range(6, 13):
            sistema.actualizar_tiempo(dia, hora)
            print(f"\n🕗 --- {hora}:00 {'AM' if hora < 12 else 'PM'} ---")
            
            # [cite_start]Si son las 12:00 PM, se ejecuta el cierre contable [cite: 33]
            if hora == 12:
                print("🛑 Hora del cierre. Deteniendo asignaciones momentáneamente...")
                sistema.cierre_contable_diario()
            
            # Simulación: Cada 'hora' dura 3 segundos reales para ver los logs
            time.sleep(3)

    # 4. Finalización
    print("\n🏁 Fin de los días simulados. Deteniendo sistema...")
    
    # Detener hilos
    for t in taxis: t.parar = True
    for c in clientes: c.parar = True
    
    # Esperar a que terminen (join con timeout corto por si alguno está durmiendo)
    for t in taxis: t.join(timeout=0.1)
    for c in clientes: c.join(timeout=0.1)
    
    print("✅ Simulación terminada con éxito.")

if __name__ == "__main__":
    ejecutar_simulacion()