"""
Algoritmo de Optimización por Colonia de Hormigas (ACO) para NWJSSP
Basado en el comportamiento de las hormigas que usan feromonas para comunicarse
"""

import time
import random
import math
from read_instances import calculate_flow_time


class AntColonyOptimization:
    """
    Algoritmo ACO para NWJSSP
    
    Parámetros:
    - num_ants: número de hormigas (soluciones) en cada iteración
    - num_iterations: número de iteraciones del algoritmo
    - evaporation: tasa de evaporación de feromonas (0 < evap < 1)
    - alpha: peso de la feromona en la decisión (mayor = más exploración del camino anterior)
    - beta: peso de la información heurística (mayor = más greedy)
    """
    
    def __init__(self, n, m, operations, release_dates, num_ants=20, num_iterations=30, 
                 evaporation=0.3, alpha=1.0, beta=2.0):
        """
        Inicializa el algoritmo ACO
        
        Args:
            n: número de trabajos
            m: número de máquinas
            operations: lista de operaciones por trabajo
            release_dates: tiempos de liberación de cada trabajo
            num_ants: número de hormigas por iteración
            num_iterations: número de iteraciones
            evaporation: tasa de evaporación (0 a 1)
            alpha: peso de feromonas
            beta: peso de información heurística
        """
        self.n = n
        self.m = m
        self.operations = operations
        self.release_dates = release_dates
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.evaporation = evaporation
        self.alpha = alpha
        self.beta = beta
        
        # Matriz de feromonas: pheromone[i][j] = feromona en arista (i, j)
        # Inicializar con valor pequeño
        self.pheromone = [[0.1 for _ in range(n)] for _ in range(n)]
        
    def calculate_heuristic_value(self, job_id):
        """
        Calcula la información heurística (inverso de la prioridad)
        
        Args:
            job_id: índice del trabajo
            
        Returns:
            heuristic: valor heurístico (mayor = mejor)
        """
        total_time = sum(pt for _, pt in self.operations[job_id])
        # Heurística: preferir trabajos con menos tiempo total
        heuristic = 1.0 / (1.0 + total_time + self.release_dates[job_id])
        return heuristic
    
    def find_earliest_feasible_start(self, job_id, machine_schedule):
        """
        Encuentra el tiempo de inicio factible más temprano para un trabajo
        
        Args:
            job_id: índice del trabajo
            machine_schedule: diccionario con ocupación de máquinas
            
        Returns:
            earliest_start: tiempo más temprano de inicio
        """
        earliest_time = self.release_dates[job_id]
        current_time = earliest_time
        
        for machine, processing_time in self.operations[job_id]:
            if machine in machine_schedule:
                machine_end = max((end for _, end, _ in machine_schedule[machine]), default=0)
                current_time = max(current_time, machine_end)
            current_time += processing_time
        
        # Buscar el tiempo de inicio válido
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
    
    def construct_ant_solution(self):
        """
        Construye una solución siguiendo una hormiga usando feromonas e información heurística
        
        Returns:
            job_start_times: lista con tiempos de inicio de cada trabajo
        """
        remaining_jobs = set(range(self.n))
        job_start_times = [0] * self.n
        machine_schedule = {}
        path = []
        
        while remaining_jobs:
            # Calcular probabilidades basadas en feromonas e información heurística
            probabilities = {}
            denominator = 0.0
            
            for job_id in remaining_jobs:
                # Usar feromona acumulada con trabajos anteriores
                pheromone_value = 1.0
                if path:
                    # Promedio de feromonas con trabajos anteriores
                    pheromone_value = sum(self.pheromone[prev][job_id] for prev in path) / len(path)
                
                heuristic = self.calculate_heuristic_value(job_id)
                
                # Probabilidad: (feromona^alpha) * (heurística^beta)
                probability = (pheromone_value ** self.alpha) * (heuristic ** self.beta)
                probabilities[job_id] = probability
                denominator += probability
            
            # Normalizar probabilidades
            if denominator > 0:
                probabilities = {job: prob / denominator for job, prob in probabilities.items()}
            else:
                # Si no hay probabilidades válidas, elegir aleatoriamente
                prob = 1.0 / len(remaining_jobs)
                probabilities = {job: prob for job in remaining_jobs}
            
            # Seleccionar trabajo según probabilidades
            jobs_list = list(remaining_jobs)
            probs_list = [probabilities[j] for j in jobs_list]
            selected_job = random.choices(jobs_list, weights=probs_list, k=1)[0]
            
            path.append(selected_job)
            remaining_jobs.remove(selected_job)
            
            # Encontrar tiempo de inicio factible
            start_time = self.find_earliest_feasible_start(selected_job, machine_schedule)
            job_start_times[selected_job] = start_time
            
            # Actualizar programa de máquinas
            current_time = start_time
            for machine, processing_time in self.operations[selected_job]:
                if machine not in machine_schedule:
                    machine_schedule[machine] = []
                
                machine_schedule[machine].append((current_time, current_time + processing_time, selected_job))
                current_time += processing_time
        
        return job_start_times, path
    
    def update_pheromone(self, solutions_and_paths, best_flow_time):
        """
        Actualiza la matriz de feromonas basada en las soluciones encontradas
        
        Args:
            solutions_and_paths: lista de (solución, camino, flow_time)
            best_flow_time: mejor flow_time encontrado hasta ahora
        """
        # Evaporación
        for i in range(self.n):
            for j in range(self.n):
                self.pheromone[i][j] *= (1.0 - self.evaporation)
        
        # Depositar feromona de las soluciones
        for solution, path, flow_time in solutions_and_paths:
            # Mejor soluciones depositan más feromona
            if flow_time > 0:
                deposit = best_flow_time / flow_time
            else:
                deposit = 1.0
            
            # Actualizar feromonas en el camino
            for i in range(len(path) - 1):
                job_i = path[i]
                job_j = path[i + 1]
                self.pheromone[job_i][job_j] += deposit
                self.pheromone[job_j][job_i] += deposit  # Simetría
    
    def solve(self):
        """
        Resuelve el problema usando ACO
        
        Returns:
            best_solution: mejor solución encontrada
            best_flow_time: valor de la función objetivo
            computation_time: tiempo de ejecución en milisegundos
        """
        start_computation = time.time()
        
        best_solution = None
        best_flow_time = float('inf')
        
        for iteration in range(self.num_iterations):
            solutions_and_paths = []
            
            # Construir soluciones con cada hormiga
            for ant in range(self.num_ants):
                solution, path = self.construct_ant_solution()
                flow_time, _ = calculate_flow_time(solution, self.operations, self.release_dates)
                solutions_and_paths.append((solution, path, flow_time))
                
                # Actualizar mejor solución
                if flow_time < best_flow_time:
                    best_solution = solution.copy()
                    best_flow_time = flow_time
            
            # Actualizar feromonas
            self.update_pheromone(solutions_and_paths, best_flow_time)
        
        end_computation = time.time()
        computation_time = (end_computation - start_computation) * 1000  # en milisegundos
        
        return best_solution, best_flow_time, computation_time
