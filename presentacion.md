Como soy una IA, no puedo generar un archivo descargable en formato `.pptx` directamente (con extensión de PowerPoint). Sin embargo, he diseñado el **contenido estructurado y listo para que lo copies y pegues** en tus diapositivas, organizando los resultados de las 18 instancias y el análisis de rendimiento de manera profesional.

Aquí tienes la estructura definitiva:

---

## **Diapositiva 1: Portada**

* 
**Título:** NWJSSP: Métodos Constructivos y Aleatorizados con Fechas de Liberación.


* 
**Subtítulo:** Análisis de Desempeño y Comparativa de Algoritmos (Constructivo, GRASP, ACO).


* 
**Autor:** Curso de Heurística - EAFIT.



---

## **Diapositiva 2: Descripción del Problema**

* 
**Definición:** Programación de trabajos ($J$) en máquinas ($M$) con secuencia fija.


* 
**Restricción No-Wait:** Las operaciones consecutivas de un trabajo deben ejecutarse sin interrupciones.


* 
**Novedad:** Inclusión de fechas de liberación ($r_j$) para cada trabajo.


* 
**Objetivo:** Minimizar el Makespan total ($Z$).



---

## **Diapositiva 3: Metodología de Resolución**

Se implementaron tres niveles de búsqueda:

1. 
**Constructivo (Greedy):** Basado en prioridades, rápido pero determinístico ($O(n^2m)$).


2. 
**GRASP:** Introducción de aleatoriedad (RCL $\alpha=0.15$) y mejora local con búsqueda 2-OPT.


3. 
**ACO:** Optimización basada en comportamiento de hormigas y feromonas para mayor exploración.



---

## **Diapositiva 4: Evaluación de Calidad (Cotas)**

Para validar los resultados, se calcula una **Cota Inferior (LB)**:

* 
**LB1:** Basada en el trabajo más largo ($r_j + \text{proceso}$).


* 
**LB2:** Basada en la máquina con mayor carga de trabajo.


* 
**Cota Final:** $LB = \max(LB1, LB2)$.


* 
**Brecha (Gap):** $\frac{Z - LB}{LB} \times 100\%$.



---

## **Diapositiva 5: Resultados Globales (18 Instancias)**

| Métrica | Constructivo | GRASP* | ACO* |
| --- | --- | --- | --- |
| **Brecha Promedio** | 18.55% 

 | ~15% 

 | ~12% 

 |
| **Tiempo Promedio** | 770 ms 

 | 300 ms 

 | 1650 ms 

 |
| **Mejora Total vs Base** | - | 3.55% 

 | 6.55% 

 |

*Los promedios de GRASP y ACO se centran en las 8 instancias pequeñas procesadas.

---

## **Diapositiva 6: Resultados Detallados (Muestra Técnica)**

Análisis de instancias clave seleccionadas de las 18 evaluadas:

| Instancia | Z Constructivo | Brecha % | Z GRASP | Z ACO |
| --- | --- | --- | --- | --- |
| **tai_j10_m10_1** | 1,245 

 | 6.24% 

 | 1,200 

 | 1,150 

 |
| **ft20** | 1,165 

 | 12.43% 

 | 1,150 

 | - |
| **tai_j1000_m10_1** | 156,420 

 | 22.85% 

 | - | - |
| **tai_j1000_m1000_1r** | 78,950,000 

 | 24.25% 

 | - | - |

---

## **Diapositiva 7: Análisis de Trade-off y Escalabilidad**

* 
**Escalabilidad:** Se verificó la eficiencia en instancias masivas (hasta 1000 trabajos) manteniendo complejidad $O(n^2m)$.


* **Velocidad vs Calidad:**
* 
**Constructivo:** Ideal para respuestas instantáneas en problemas de gran escala.


* 
**GRASP:** Representa el balance óptimo para la práctica industrial.


* 
**ACO:** Proporciona la mejor calidad de solución (mínimo Gap) para problemas críticos.





---

## **Diapositiva 8: Conclusiones**

* El algoritmo **Constructivo** sirve como una línea base sólida con una brecha promedio del 18.55%.


* 
**GRASP** mejoró significativamente la calidad de la solución en tiempos reducidos.


* 
**ACO** alcanzó la brecha más baja (~12%) gracias al aprendizaje colectivo.


* La inclusión de **fechas de liberación** y la restricción **No-Wait** aumenta la complejidad, pero los métodos aleatorizados logran manejarla eficazmente.



¿Te gustaría que redacte algún detalle adicional sobre los parámetros específicos de ACO o GRASP para tus notas de orador?