"""
Algoritmo GRASP para NWJSSP
GRASP = Greedy Randomized Adaptive Search Procedure
Combina construcción greedy aleatoria con búsqueda local
"""

import time
import random
from read_instances import calculate_flow_time


class GRASP:
    """
    Algoritmo GRASP para NWJSSP
    
    Parámetros:
    - alpha: parámetro de restricción de candidatos (0 <= alpha <= 1)
      alpha=0: construcción aleatoria pura
      alpha=1: construcción greedy determinística
    - nsol: número de soluciones a generar en cada iteración
    """
    
    def __init__(self, n, m, operations, release_dates, alpha=0.15, nsol=50):
        """
        Inicializa el algoritmo GRASP
        
        Args:
            n: número de trabajos
            m: número de máquinas
            operations: lista de operaciones por trabajo
            release_dates: tiempos de liberación de cada trabajo
            alpha: parámetro de restricción de candidatos (0.0 a 1.0)
            nsol: número de soluciones a generar
        """
        self.n = n
        self.m = m
        self.operations = operations
        self.release_dates = release_dates
        self.alpha = alpha
        self.nsol = nsol
        
    def calculate_job_priority(self, job_id, remaining_jobs):
        """
        Calcula la prioridad de un trabajo para la construcción greedy
        
        Args:
            job_id: índice del trabajo
            remaining_jobs: conjunto de trabajos aún no programados
            
        Returns:
            priority: valor de prioridad (menor = mayor prioridad)
        """
        if job_id not in remaining_jobs:
            return float('inf')
        
        # Criterio: combinar fecha de liberación y suma de tiempos
        total_time = sum(pt for _, pt in self.operations[job_id])
        priority = (self.release_dates[job_id], total_time)
        return priority
    
    def find_earliest_feasible_start(self, job_id, job_start_times, machine_schedule):
        """
        Encuentra el tiempo de inicio factible más temprano para un trabajo
        
        Args:
            job_id: índice del trabajo
            job_start_times: lista con tiempos de inicio actuales
            machine_schedule: diccionario con ocupación de máquinas
            
        Returns:
            earliest_start: tiempo más temprano de inicio
        """
        # Respetar fecha de liberación
        earliest_time = self.release_dates[job_id]
        current_time = earliest_time
        
        # Considerar disponibilidad de máquinas
        for machine, processing_time in self.operations[job_id]:
            if machine in machine_schedule:
                # Encontrar cuándo la máquina estará disponible
                machine_end = max((end for _, end, _ in machine_schedule[machine]), default=0)
                current_time = max(current_time, machine_end)
            
            current_time += processing_time
        
        # Buscar el tiempo de inicio válido más temprano
        for trial_start in range(earliest_time, max(earliest_time, current_time) + 1000):
            if self._is_valid_start(job_id, trial_start, machine_schedule):
                return trial_start
        
        return earliest_time
    
    def _is_valid_start(self, job_id, start_time, machine_schedule):
        """Verifica si un tiempo de inicio es válido"""
        if start_time < self.release_dates[job_id]:
            return False
        
        current_time = start_time
        for machine, processing_time in self.operations[job_id]:
            op_start = current_time
            op_end = current_time + processing_time
            
            if machine in machine_schedule:
                for prev_start, prev_end, _ in machine_schedule[machine]:
                    if (op_start < prev_end and op_end > prev_start):
                        return False
            
            current_time = op_end
        
        return True
    
    def construct_solution_greedy_randomized(self):
        """
        Construye una solución usando el procedimiento greedy randomizado
        
        Returns:
            job_start_times: lista con tiempos de inicio de cada trabajo
        """
        remaining_jobs = set(range(self.n))
        job_start_times = [0] * self.n
        machine_schedule = {}
        
        while remaining_jobs:
            # Calcular prioridades de trabajos disponibles
            priorities = {j: self.calculate_job_priority(j, remaining_jobs) 
                         for j in remaining_jobs}
            
            # Ordenar por prioridad
            sorted_jobs = sorted(remaining_jobs, key=lambda j: priorities[j])
            
            # Crear lista de candidatos restringida (RCL)
            num_candidates = max(1, int(self.alpha * len(sorted_jobs)))
            rcl = sorted_jobs[:num_candidates]
            
            # Seleccionar aleatoriamente de la RCL
            selected_job = random.choice(rcl)
            remaining_jobs.remove(selected_job)
            
            # Encontrar tiempo de inicio factible
            start_time = self.find_earliest_feasible_start(selected_job, job_start_times, machine_schedule)
            job_start_times[selected_job] = start_time
            
            # Actualizar programa de máquinas
            current_time = start_time
            for machine, processing_time in self.operations[selected_job]:
                if machine not in machine_schedule:
                    machine_schedule[machine] = []
                
                machine_schedule[machine].append((current_time, current_time + processing_time, selected_job))
                current_time += processing_time
        
        return job_start_times
    
    def local_search_2opt(self, job_start_times):
        """
        Búsqueda local simple: intenta intercambiar pares de trabajos
        
        Args:
            job_start_times: lista con tiempos de inicio
            
        Returns:
            improved_solution: solución mejorada
        """
        best_solution = job_start_times.copy()
        best_flow_time, _ = calculate_flow_time(best_solution, self.operations, self.release_dates)
        
        improved = True
        iterations = 0
        max_iterations = min(3, self.n)  # máximo 3 iteraciones
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for i in range(self.n):
                for j in range(i + 1, min(i + 4, self.n)):  # solo revisar 4 siguientes 
                    # Crear solución vecina intercambiando tiempos de inicio
                    neighbor = best_solution.copy()
                    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                    
                    # Evaluar solución vecina
                    neighbor_flow, _ = calculate_flow_time(neighbor, self.operations, self.release_dates)
                    
                    if neighbor_flow < best_flow_time:
                        best_solution = neighbor
                        best_flow_time = neighbor_flow
                        improved = True
                        break
                
                if improved:
                    break
        
        return best_solution
    
    def solve(self):
        """
        Resuelve el problema usando GRASP
        
        Returns:
            best_solution: mejor solución encontrada
            best_flow_time: valor de la función objetivo
            computation_time: tiempo de ejecución en milisegundos
        """
        start_computation = time.time()
        
        best_solution = None
        best_flow_time = float('inf')
        
        # Realizar múltiples iteraciones GRASP
        for iteration in range(self.nsol):
            # Construcción greedy randomizada
            solution = self.construct_solution_greedy_randomized()
            
            # Búsqueda local
            solution = self.local_search_2opt(solution)
            
            # Evaluar solución
            flow_time, _ = calculate_flow_time(solution, self.operations, self.release_dates)
            
            if flow_time < best_flow_time:
                best_solution = solution
                best_flow_time = flow_time
        
        end_computation = time.time()
        computation_time = (end_computation - start_computation) * 1000  # en milisegundos
        
        return best_solution, best_flow_time, computation_time
