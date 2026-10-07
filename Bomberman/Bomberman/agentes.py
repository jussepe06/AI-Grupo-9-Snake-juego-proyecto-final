"""
agentes.py -- Agentes del Bomberman.

Todos los agentes tienen la MISMA interfaz:
    agente.decidir(estado, mi_id)  ->  una acción (texto)
y el atributo agente.nodos_expandidos (sirve para BFS y A* en pasos posteriores).
"""
import random
from bomberman_env import ACCIONES


class AgenteAleatorio:
    """Modo base: elige una acción al azar. Sirve para saber si las técnicas aportan algo."""
    nombre = "Aleatorio"

    def __init__(self, semilla=None):
        self.rng = random.Random(semilla)   # su propio generador: resultados reproducibles
        self.nodos_expandidos = 0           # no busca, siempre 0

    def decidir(self, estado, mi_id):
        return self.rng.choice(ACCIONES)


# Registro: la app y los experimentos eligen agentes por nombre
AGENTES = {
    "Aleatorio": AgenteAleatorio,
}
