
import os

def read_instance_for_lower_bound(filepath):
    """
    Lee una instancia y extrae solo la información necesaria para la cota inferior.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
        # Primera línea: n, m
        n, m = map(int, lines[0].strip().split())
        
        all_operations = []
        
        # Leer las n líneas de trabajos
        for i in range(n):
            parts = list(map(int, lines[i + 1].strip().split()))
            
            # Extraer las operaciones (pares de máquina, tiempo)
            job_ops = []
            for j in range(m):
                machine = parts[j * 2]
                processing_time = parts[j * 2 + 1]
                job_ops.append((machine, processing_time))
            all_operations.append(job_ops)
            
    return all_operations

def calculate_lower_bound(operations):
    """
    Calcula una cota inferior simple para el flow time total.
    Es la suma de los tiempos de procesamiento de todas las operaciones de todos los trabajos.
    """
    total_processing_time = 0
    for job_ops in operations:
        for _, processing_time in job_ops:
            total_processing_time += processing_time
    return total_processing_time

def main():
    """
    Calcula y muestra la cota inferior para todas las instancias en la carpeta 'instances'.
    """
    instance_folder = 'instances'
    print("Calculando Cotas Inferiores (Lower Bounds) para el Flow Time Total:")
    print("-" * 60)
    
    instance_files = sorted(os.listdir(instance_folder))
    
    results = {}
    
    for filename in instance_files:
        if filename.endswith('.txt'):
            filepath = os.path.join(instance_folder, filename)
            try:
                operations = read_instance_for_lower_bound(filepath)
                lower_bound = calculate_lower_bound(operations)
                results[filename] = lower_bound
                print(f"{filename:<25}: {lower_bound}")
            except Exception as e:
                print(f"Error procesando {filename}: {e}")

    print("-" * 60)
    return results

if __name__ == "__main__":
    main()
