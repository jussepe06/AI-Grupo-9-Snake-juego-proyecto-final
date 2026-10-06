# Proyecto Snake Autónomo - Grupo 9

**Problema y quién lo sufre:** El diseño de rutas óptimas en entornos dinámicos y cerrados genera colisiones fatales. Lo sufren sistemas de enrutamiento automatizado y logística de almacenes (representado aquí mediante el entorno Snake).

**Modo base:** Agente Aleatorio / Control Manual. Se elige la dirección sin planificación algorítmica ni evaluación del entorno.

**Técnicas comparadas:**
*   **Parte 1:** Búsqueda ciega en anchura (BFS) vs. Búsqueda informada $A*) con heurística de Manhattan y penalización de callejones.
*   **Parte 2:** (Semana 15) Entrenamiento de clasificadores (KNN, Decision Trees, MLP) para imitar la toma de decisiones de A* a partir de estados almacenados.

**Tabla de Resultados:**
*(Ejecuta el script `main.py` para rellenar los datos precisos de las corridas simuladas. Al iniciar, el juego imprime esta tabla automáticamente en la consola)*

| Técnica | Longitud Máxima | % Partidas Ganadas | Nodos Expandidos / Jugada | Tiempo (ms/jugada) | Corridas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Base (Aleatorio) | [Dato] | [Dato]% | N/A | [Dato] | 10 |
| Búsqueda BFS | [Dato] | [Dato]% | [Miles de nodos] | [Dato] | 10 |
| Búsqueda A* | [Dato] | [Dato]% | [Cientos de nodos] | [Dato] | 10 |

**Cómo ejecutarlo:**
*   **En línea (Demostración):** [INSERTA_TU_ENLACE_DE_GITHUB_PAGES_O_ITCH.IO]
*   **Localmente:** Instalar `pip install pygame asyncio` y ejecutar `python main.py`. Para compilar localmente en web, usar `pygbag main.py`.

**Uso de IA:**
El código base asíncrono de Pygame para el despliegue en Pygbag y la estructura de los algoritmos de búsqueda fueron generados con Antigravity IDE. Se ajustaron manualmente las heurísticas de evasión de cuerpo del agente A*.

**Roles:**
*   [Tu Apellido, Nombre]: Integración del agente A*, adaptación asíncrona del bucle y compilación en Pygbag.
*   [Compañero 2]: Programación del Agente BFS, entorno Pygame y telemetría de nodos expandidos.
*   [Compañero 3]: Diseño del modo base aleatorio, recopilación de métricas y redacción del README.
