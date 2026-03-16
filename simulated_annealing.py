"""
Algoritmo Simulated Annealing (SA) para NWJSSP
Basado en el proceso de enfriamiento de metales
Rápido, simple y muy efectivo
"""

import time
import random
import math
from read_instances import calculate_flow_time


class SimulatedAnnealing:
    """
    Algoritmo Simulated Annealing para NWJSSP
    
    Idea: Simula el enfriamiento de un metal caliente
    - Al principio (caliente): acepta soluciones malas (explora)
    - Al final (frío): solo acepta soluciones mejores (explota)
    
    Parámetros:
    - initial_temp: temperatura inicial
    - cooling_rate: tasa de enfriamiento (0.95 = enfría 5% cada iteración)
    - iterations_per_temp: cuántas iteraciones en cada temperatura
    """
    
    def __init__(self, n, m, operations, release_dates, initial_temp=100.0, 
                 cooling_rate=0.95, iterations_per_temp=50):
        """
        Inicializa Simulated Annealing
        
        Args:
            n: número de trabajos
            m: número de máquinas
            operations: lista de operaciones por trabajo
            release_dates: tiempos de liberación de cada trabajo
            initial_temp: temperatura inicial (100)
            cooling_rate: tasa de enfriamiento (0.95)
            iterations_per_temp: iteraciones por nivel de temperatura (50)
        """
        self.n = n
        self.m = m
        self.operations = operations
        self.release_dates = release_dates
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.iterations_per_temp = iterations_per_temp
        
    def construct_initial_solution(self):
        """
        Construye una solución inicial usando Constructivo (greedy)
        
        Returns:
            job_start_times: lista con tiempos de inicio
        """
        remaining_jobs = set(range(self.n))
        job_start_times = [0] * self.n
        machine_schedule = {}
        
        # Ordenar por tiempo total (greedy simple)
        job_order = sorted(range(self.n), 
                          key=lambda j: sum(pt for _, pt in self.operations[j]))
        
        for job_id in job_order:
            # Encontrar tiempo de inicio factible
            start_time = self.find_earliest_feasible_start(job_id, machine_schedule)
            job_start_times[job_id] = start_time
            
            # Actualizar máquinas
            current_time = start_time
            for machine, processing_time in self.operations[job_id]:
                if machine not in machine_schedule:
                    machine_schedule[machine] = []
                machine_schedule[machine].append((current_time, current_time + processing_time, job_id))
                current_time += processing_time
        
        return job_start_times
    
    def find_earliest_feasible_start(self, job_id, machine_schedule):
        """Encuentra el tiempo de inicio más temprano"""
        earliest_time = self.release_dates[job_id]
        current_time = earliest_time
        
        for machine, processing_time in self.operations[job_id]:
            if machine in machine_schedule:
                machine_end = max((end for _, end, _ in machine_schedule[machine]), default=0)
                current_time = max(current_time, machine_end)
            current_time += processing_time
        
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
    
    def generate_neighbor(self, solution):
        """
        Genera una solución vecina intercambiando dos trabajos
        
        Este es el operador de vecindario: 2-OPT simple
        Intercambia tiempos de inicio de dos trabajos al azar
        
        Args:
            solution: solución actual
            
        Returns:
            neighbor: solución vecina
        """
        neighbor = solution.copy()
        
        # Seleccionar dos trabajos al azar
        i = random.randint(0, self.n - 1)
        j = random.randint(0, self.n - 1)
        
        while i == j:
            j = random.randint(0, self.n - 1)
        
        # Intercambiar tiempos de inicio
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        
        return neighbor
    
    def accept_solution(self, current_cost, neighbor_cost, temperature):
        """
        Decide si aceptar una solución vecina
        
        Algoritmo:
        - Si mejor: SIEMPRE aceptar
        - Si peor: aceptar con probabilidad exp(-(peor_costo) / temperatura)
        
        Args:
            current_cost: makespan actual
            neighbor_cost: makespan del vecino
            temperature: temperatura actual
            
        Returns:
            True si acepta, False si rechaza
        """
        if neighbor_cost < current_cost:
            # Mejor solución: aceptar siempre
            return True
        else:
            # Peor solución: aceptar con probabilidad
            delta = neighbor_cost - current_cost
            probability = math.exp(-delta / temperature)
            return random.random() < probability
    
    def solve(self):
        """
        Resuelve el problema usando Simulated Annealing
        
        Algoritmo:
        1. Construir solución inicial (Constructivo)
        2. Mientras temperatura > threshold:
           a. Repetir iterations_per_temp veces:
              - Generar vecino (2-OPT)
              - Si mejora: aceptar
              - Si empeora: aceptar con probabilidad e^(-delta/T)
           b. Enfriar: T = T * cooling_rate
        3. Devolver mejor solución encontrada
        
        Ventajas sobre ACO:
        - MUCHO más rápido (sin matriz de feromonas)
        - Parámetros simples (temperatura, enfriamiento)
        - Convergencia garantizada
        
        Returns:
            best_solution: mejor solución encontrada
            best_flow_time: valor de la función objetivo
            computation_time: tiempo de ejecución en milisegundos
        """
        start_computation = time.time()
        
        # Solución inicial (Constructivo)
        current_solution = self.construct_initial_solution()
        current_cost, _ = calculate_flow_time(current_solution, self.operations, self.release_dates)
        
        best_solution = current_solution.copy()
        best_cost = current_cost
        
        temperature = self.initial_temp
        
        # Enfriamiento gradual
        while temperature > 0.01:  # Umbral de temperatura
            
            # Múltiples intentos en este nivel de temperatura
            for iteration in range(self.iterations_per_temp):
                # Generar vecino (intercambiar dos trabajos)
                neighbor_solution = self.generate_neighbor(current_solution)
                neighbor_cost, _ = calculate_flow_time(neighbor_solution, self.operations, self.release_dates)
                
                # Decidir si aceptar
                if self.accept_solution(current_cost, neighbor_cost, temperature):
                    current_solution = neighbor_solution
                    current_cost = neighbor_cost
                    
                    # Actualizar mejor si es mejor
                    if neighbor_cost < best_cost:
                        best_solution = neighbor_solution.copy()
                        best_cost = neighbor_cost
            
            # Enfriar: reducir temperatura
            temperature *= self.cooling_rate
        
        end_computation = time.time()
        computation_time = (end_computation - start_computation) * 1000
        
        return best_solution, best_cost, computation_time