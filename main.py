"""
Script principal para ejecutar los tres algoritmos de NWJSSP
Genera archivos de resultados en formato Excel según especificaciones del curso
"""

import os
import glob
import time
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from constructive import ConstructiveAlgorithm
from grasp import GRASP
from aco import AntColonyOptimization
from read_instances import read_nwjssp_instance, calculate_flow_time


# ====== PARÁMETROS DE LOS ALGORITMOS ======
# ALGORITMO CONSTRUCTIVO
CONSTRUCTIVE_PARAMS = {}

# ALGORITMO GRASP 1 - PARÁMETROS OPTIMIZADOS PARA VELOCIDAD
GRASP_ALPHA = 0.15      # Parámetro de restricción de candidatos
GRASP_NSOL = 15         # REDUCIDO: Número de soluciones a generar (era 50)


# ALGORITMO ACO - PARÁMETROS OPTIMIZADOS PARA VELOCIDAD
ACO_NUM_ANTS = 10       # REDUCIDO: Número de hormigas por iteración (era 20)
ACO_NUM_ITERATIONS = 10 # REDUCIDO: Número de iteraciones (era 30)
ACO_EVAPORATION = 0.3   # Tasa de evaporación de feromonas
ACO_ALPHA = 1.0         # Peso de feromonas
ACO_BETA = 2.0          # Peso de información heurística

# ====== DIRECTORIO DE INSTANCIAS ======
INSTANCES_DIR = "instances"  # Directorio con archivos .txt de instancias


def create_results_workbook(algorithm_name):
    """
    Crea un nuevo workbook para guardar resultados
    
    Args:
        algorithm_name: nombre del algoritmo
        
    Returns:
        workbook: objeto Workbook de openpyxl
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    return wb


def get_column_letter(col_num):
    """
    Convierte número de columna a letra Excel válida
    Args:
        col_num: número de columna (0-indexado)
    Returns:
        letra de columna (A, B, C, ..., Z, AA, AB, ...)
    """
    col_letter = ""
    col = col_num
    while col >= 0:
        col_letter = chr(65 + (col % 26)) + col_letter
        col = col // 26 - 1
        if col < 0:
            break
    return col_letter


def add_results_sheet(workbook, instance_name, flow_time, computation_time, job_start_times):
    """
    Añade una hoja de resultados para una instancia
    
    Args:
        workbook: objeto Workbook
        instance_name: nombre de la instancia
        flow_time: valor de la función objetivo
        computation_time: tiempo de cómputo en milisegundos
        job_start_times: lista con tiempos de inicio de cada trabajo
    """
    # Crear nueva hoja
    ws = workbook.create_sheet(instance_name)
    
    # Primera fila: Z y tiempo de cómputo
    ws['A1'] = int(flow_time)
    ws['B1'] = int(round(computation_time))
    
    # Segunda fila: tiempos de inicio de trabajos
    for idx, start_time in enumerate(job_start_times):
        col_letter = get_column_letter(idx)
        cell_ref = f'{col_letter}2'
        ws[cell_ref] = int(start_time)
    
    # Formateo básico
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in [ws['A1'], ws['B1']]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Ajustar ancho de columnas
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 15
    for idx in range(len(job_start_times)):
        col_letter = get_column_letter(idx)
        ws.column_dimensions[col_letter].width = 12


def run_constructive_algorithm(n, m, operations, release_dates):
    """
    Ejecuta el algoritmo constructivo
    
    Args:
        n, m, operations, release_dates: datos del problema
        
    Returns:
        solution, flow_time, computation_time
    """
    algo = ConstructiveAlgorithm(n, m, operations, release_dates)
    solution, flow_time, computation_time = algo.solve()
    return solution, flow_time, computation_time


def run_grasp_algorithm(n, m, operations, release_dates, alpha=GRASP_ALPHA, nsol=GRASP_NSOL):
    """
    Ejecuta el algoritmo GRASP
    
    Args:
        n, m, operations, release_dates: datos del problema
        alpha: parámetro de restricción de candidatos
        nsol: número de soluciones
        
    Returns:
        solution, flow_time, computation_time
    """
    algo = GRASP(n, m, operations, release_dates, alpha=alpha, nsol=nsol)
    solution, flow_time, computation_time = algo.solve()
    return solution, flow_time, computation_time


def run_aco_algorithm(n, m, operations, release_dates, num_ants=ACO_NUM_ANTS, 
                      num_iterations=ACO_NUM_ITERATIONS):
    """
    Ejecuta el algoritmo ACO
    
    Args:
        n, m, operations, release_dates: datos del problema
        num_ants: número de hormigas
        num_iterations: número de iteraciones
        
    Returns:
        solution, flow_time, computation_time
    """
    algo = AntColonyOptimization(n, m, operations, release_dates, 
                                  num_ants=num_ants, 
                                  num_iterations=num_iterations,
                                  evaporation=ACO_EVAPORATION,
                                  alpha=ACO_ALPHA,
                                  beta=ACO_BETA)
    solution, flow_time, computation_time = algo.solve()
    return solution, flow_time, computation_time


def process_instance(instance_file, algorithm_func, **algo_kwargs):
    """
    Procesa una instancia con un algoritmo específico
    
    Args:
        instance_file: ruta del archivo de instancia
        algorithm_func: función del algoritmo a ejecutar
        **algo_kwargs: parámetros adicionales del algoritmo
        
    Returns:
        tuple: (nombre_instancia, solution, flow_time, computation_time) o None si hay error
    """
    try:
        # Leer instancia
        n, m, operations, release_dates, L = read_nwjssp_instance(instance_file)
        
        # Ejecutar algoritmo
        solution, flow_time, computation_time = algorithm_func(n, m, operations, release_dates, **algo_kwargs)
        
        # Obtener nombre de instancia
        instance_name = os.path.splitext(os.path.basename(instance_file))[0]
        
        return instance_name, solution, flow_time, computation_time
    
    except Exception as e:
        print(f"Error procesando {instance_file}: {str(e)}")
        return None


def main():
    """
    Función principal: ejecuta todos los algoritmos en todas las instancias
    """
    print("=" * 60)
    print("NWJSSP - Algoritmos Constructivos y Aleatorizados")
    print("=" * 60)
    
    # Buscar archivos de instancias
    instance_files = glob.glob(os.path.join(INSTANCES_DIR, "*.txt"))
    instance_files.sort()
    
    if not instance_files:
        print(f"Error: No se encontraron archivos de instancias en {INSTANCES_DIR}")
        return
    
    print(f"Se encontraron {len(instance_files)} instancias")
    print()
    
    # ====== ALGORITMO 1: CONSTRUCTIVO ======
    print("Ejecutando Algoritmo Constructivo...")
    wb_constructive = create_results_workbook("Constructive")
    
    for instance_file in instance_files:
        result = process_instance(instance_file, run_constructive_algorithm)
        if result:
            instance_name, solution, flow_time, computation_time = result
            print(f"  {instance_name}: Z={flow_time:.0f}, Tiempo={computation_time:.2f}ms")
            add_results_sheet(wb_constructive, instance_name, flow_time, computation_time, solution)
    
    output_file_constructive = f"NWJSSP_ArturoMurgueytio_Constructivo.xlsx"
    wb_constructive.save(output_file_constructive)
    print(f"Resultados guardados en {output_file_constructive}\n")
    
    # ====== ALGORITMO 2: GRASP ======
    print("Ejecutando Algoritmo GRASP...")
    wb_grasp = create_results_workbook("GRASP")
    
    for instance_file in instance_files:
        result = process_instance(instance_file, run_grasp_algorithm, 
                                 alpha=GRASP_ALPHA, nsol=GRASP_NSOL)
        if result:
            instance_name, solution, flow_time, computation_time = result
            print(f"  {instance_name}: Z={flow_time:.0f}, Tiempo={computation_time:.2f}ms")
            add_results_sheet(wb_grasp, instance_name, flow_time, computation_time, solution)
    
    output_file_grasp = f"NWJSSP_ArturoMurgueytio_GRASP.xlsx"
    wb_grasp.save(output_file_grasp)
    print(f"Resultados guardados en {output_file_grasp}\n")
    
    # ====== ALGORITMO 3: ACO ======
    print("Ejecutando Algoritmo ACO...")
    wb_aco = create_results_workbook("ACO")
    
    for instance_file in instance_files:
        result = process_instance(instance_file, run_aco_algorithm,
                                 num_ants=ACO_NUM_ANTS,
                                 num_iterations=ACO_NUM_ITERATIONS)
        if result:
            instance_name, solution, flow_time, computation_time = result
            print(f"  {instance_name}: Z={flow_time:.0f}, Tiempo={computation_time:.2f}ms")
            add_results_sheet(wb_aco, instance_name, flow_time, computation_time, solution)
    
    output_file_aco = f"NWJSSP_ArturoMurgueytio_ACO.xlsx"
    wb_aco.save(output_file_aco)
    print(f"Resultados guardados en {output_file_aco}\n")
    
    print("=" * 60)
    print("Ejecución completada exitosamente")
    print("=" * 60)


if __name__ == "__main__":
    main()
