"""
Algoritmo Constructivo Determinístico para NWJSSP
Utiliza una estrategia greedy basada en tiempos de procesamiento
y fechas de liberación para construir una solución.
"""

import time
from read_instances import calculate_flow_time, is_feasible_solution


class ConstructiveAlgorithm:
    """
    Algoritmo constructivo determinístico para NWJSSP
    Utiliza una regla de prioridad: ordenar trabajos por fecha de liberación
    y luego por suma de tiempos de procesamiento (SPT - Shortest Processing Time)
    """
    
    def __init__(self, n, m, operations, release_dates):
        """
        Inicializa el algoritmo constructivo
        
        Args:
            n: número de trabajos
            m: número de máquinas
            operations: lista de operaciones por trabajo
            release_dates: tiempos de liberación de cada trabajo
        """
        self.n = n
        self.m = m
        self.operations = operations
        self.release_dates = release_dates
        
    def calculate_priority(self, job_id):
        """
        Calcula la prioridad de un trabajo
        Criterio: Fecha de liberación (primaria), suma de tiempos (secundaria)
        
        Args:
            job_id: índice del trabajo
            
        Returns:
            tupla (release_date, total_processing_time) para ordenamiento
        """
        total_time = sum(pt for _, pt in self.operations[job_id])
        return (self.release_dates[job_id], total_time)
    
    def find_earliest_start_time(self, job_id, machine_schedule):
        """
        Encuentra el tiempo más temprano en que puede iniciar un trabajo
        respetando su fecha de liberación y disponibilidad de máquinas
        
        Args:
            job_id: índice del trabajo
            machine_schedule: diccionario con ocupación de máquinas
            
        Returns:
            earliest_start: tiempo más temprano de inicio
        """
        earliest_start = self.release_dates[job_id]
        current_time = earliest_start
        
        # Simular el procesamiento de todas las operaciones
        for machine, processing_time in self.operations[job_id]:
            # Encontrar cuándo la máquina estará disponible
            if machine in machine_schedule:
                # Buscar el último evento en esta máquina
                latest_end = max((end for _, end, _ in machine_schedule[machine]), default=0)
                current_time = max(current_time, latest_end)
            
            current_time += processing_time
        
        # El trabajo debe iniciar de forma que todas sus operaciones respeten
        # la disponibilidad de máquinas
        return self._calculate_valid_start_time(job_id, machine_schedule)
    
    def _calculate_valid_start_time(self, job_id, machine_schedule):
        """
        Calcula el tiempo de inicio válido para un trabajo considerando
        todas sus operaciones y la disponibilidad de máquinas
        
        Args:
            job_id: índice del trabajo
            machine_schedule: diccionario con ocupación de máquinas
            
        Returns:
            start_time: tiempo de inicio válido
        """
        # Buscar el menor tiempo en que el trabajo puede iniciar
        start_time = self.release_dates[job_id]
        
        # Intentar diferentes tiempos de inicio hasta encontrar uno válido
        # Límite máximo reducido para optimizar
        for trial_start in range(start_time, start_time + 1000):
            if self._is_valid_start_time(job_id, trial_start, machine_schedule):
                return trial_start
        
        # Si no se encuentra, devolver el tiempo de liberación
        return start_time
    
    def _is_valid_start_time(self, job_id, start_time, machine_schedule):
        """
        Verifica si un tiempo de inicio es válido para un trabajo
        
        Args:
            job_id: índice del trabajo
            start_time: tiempo de inicio a verificar
            machine_schedule: diccionario con ocupación de máquinas
            
        Returns:
            valid: booleano indicando si el tiempo es válido
        """
        if start_time < self.release_dates[job_id]:
            return False
        
        current_time = start_time
        
        for machine, processing_time in self.operations[job_id]:
            op_start = current_time
            op_end = current_time + processing_time
            
            # Verificar conflicto con otras operaciones en esta máquina
            if machine in machine_schedule:
                for prev_start, prev_end, _ in machine_schedule[machine]:
                    if (op_start < prev_end and op_end > prev_start):
                        return False
            
            current_time = op_end
        
        return True
    
    def solve(self):
        """
        Resuelve el problema usando el algoritmo constructivo
        
        Returns:
            job_start_times: lista con tiempos de inicio de cada trabajo
            flow_time: valor de la función objetivo
            computation_time: tiempo de ejecución en milisegundos
        """
        start_computation = time.time()
        
        # Ordenar trabajos por prioridad
        job_order = sorted(range(self.n), key=self.calculate_priority)
        
        # Inicializar tiempos de inicio
        job_start_times = [0] * self.n
        machine_schedule = {}  # machine -> lista de (start, end, job_id)
        
        # Construir solución insertando trabajos en orden de prioridad
        for job_id in job_order:
            # Encontrar el tiempo más temprano en que puede iniciar este trabajo
            start_time = self.find_earliest_start_time(job_id, machine_schedule)
            job_start_times[job_id] = start_time
            
            # Actualizar el programa de máquinas
            current_time = start_time
            for machine, processing_time in self.operations[job_id]:
                if machine not in machine_schedule:
                    machine_schedule[machine] = []
                
                machine_schedule[machine].append((current_time, current_time + processing_time, job_id))
                current_time += processing_time
        
        # Calcular tiempo de flujo
        flow_time, _ = calculate_flow_time(job_start_times, self.operations, self.release_dates)
        
        end_computation = time.time()
        computation_time = (end_computation - start_computation) * 1000  # en milisegundos
        
        return job_start_times, flow_time, computation_time
