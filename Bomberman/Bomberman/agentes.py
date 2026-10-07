"""
agentes.py -- Agentes del Bomberman.

Todos los agentes tienen la MISMA interfaz:
    agente.decidir(estado, mi_id)  ->  una acción (texto)
y el atributo agente.nodos_expandidos (sirve para BFS y A* en pasos posteriores).
"""
import random
import heapq
from collections import deque
from bomberman_env import ACCIONES, MURO, BLOQUE, VACIO

# Direcciones (filas, columnas) para coincidir con ACCIONES ["arriba", "abajo", "izquierda", "derecha"]
DIRS = {"arriba": (-1, 0), "abajo": (1, 0), "izquierda": (0, -1), "derecha": (0, 1)}

class AgenteAleatorio:
    """Modo base: elige una acción al azar. Sirve para saber si las técnicas aportan algo."""
    nombre = "Aleatorio"

    def __init__(self, semilla=None):
        self.rng = random.Random(semilla)
        self.nodos_expandidos = 0

    def decidir(self, estado, mi_id):
        self.nodos_expandidos = 0
        return self.rng.choice(ACCIONES)

class AgenteReflejo:
    """Agente Reactivo Simple: Actúa solo con la percepción inmediata. Evita las bombas adyacentes."""
    nombre = "Reflejo (Evasivo)"
    
    def __init__(self, semilla=None):
        self.rng = random.Random(semilla)
        self.nodos_expandidos = 0
        
    def decidir(self, estado, mi_id):
        self.nodos_expandidos = 1
        pos = estado["mi_pos"]
        mapa = estado["mapa"]
        bombas = [b["pos"] for b in estado["bombas"]]
        
        movimientos_seguros = []
        
        # Revisar las 4 direcciones
        for accion, (df, dc) in DIRS.items():
            nf, nc = pos[0] + df, pos[1] + dc
            # Si está dentro del mapa y está vacío
            if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
                if mapa[nf][nc] == VACIO:
                    # Riesgo básico: si hay una bomba directamente al lado de esa casilla
                    riesgo = any((abs(b[0]-nf) + abs(b[1]-nc)) <= 1 for b in bombas)
                    if not riesgo:
                        movimientos_seguros.append(accion)
                        
        if movimientos_seguros:
            return self.rng.choice(movimientos_seguros)
            
        # Si no hay nada seguro, tal vez poner bomba o moverse random
        return "bomba" if not bombas else self.rng.choice(["arriba", "abajo", "izquierda", "derecha", "quieto"])


class AgenteAEstrella:
    """Agente Basado en Objetivos: Usa A* para cazar al rival más cercano."""
    nombre = "A* (Cazador)"
    
    def __init__(self, semilla=None):
        self.rng = random.Random(semilla)
        self.nodos_expandidos = 0
        
    def decidir(self, estado, mi_id):
        self.nodos_expandidos = 0
        inicio = estado["mi_pos"]
        mapa = estado["mapa"]
        rivales = estado["rivales"]
        
        if not rivales:
            return "quieto"
            
        # Objetivo: El rival más cercano (Manhattan)
        objetivo = min(rivales, key=lambda r: abs(r["pos"][0]-inicio[0]) + abs(r["pos"][1]-inicio[1]))["pos"]
        
        # A* Búsqueda
        frontera = []
        heapq.heappush(frontera, (0, 0, inicio, [])) # (f, g, pos, ruta)
        visitados = {inicio: 0}
        
        mejor_accion = "quieto"
        
        while frontera:
            f, g, actual, ruta = heapq.heappop(frontera)
            self.nodos_expandidos += 1
            
            # Si estamos adyacentes al objetivo, pongamos una bomba!
            if abs(actual[0]-objetivo[0]) + abs(actual[1]-objetivo[1]) == 1:
                if len(ruta) == 0:
                    mejor_accion = "bomba"
                else:
                    mejor_accion = ruta[0]
                break
                
            for accion, (df, dc) in DIRS.items():
                nf, nc = actual[0] + df, actual[1] + dc
                vecino = (nf, nc)
                
                if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
                    if mapa[nf][nc] == VACIO or vecino == objetivo:
                        nuevo_g = g + 1
                        if vecino not in visitados or nuevo_g < visitados[vecino]:
                            visitados[vecino] = nuevo_g
                            # Heurística de Manhattan
                            h = abs(vecino[0] - objetivo[0]) + abs(vecino[1] - objetivo[1])
                            heapq.heappush(frontera, (nuevo_g + h, nuevo_g, vecino, ruta + [accion]))
                            
        # Si A* encontró una ruta válida y no decidió ya por bomba
        if mejor_accion == "quieto" and len(ruta) > 0:
            mejor_accion = ruta[0]
            
        # Si estamos atascados o sin ruta, intentar poner bomba si hay bloques cerca (opcional)
        if mejor_accion == "quieto":
             adyacentes = [mapa[inicio[0]+df][inicio[1]+dc] for df, dc in DIRS.values() if 0<=inicio[0]+df<len(mapa) and 0<=inicio[1]+dc<len(mapa[0])]
             if BLOQUE in adyacentes:
                 return "bomba"
                 
        return mejor_accion

class AgenteMinimax:
    """Agente Basado en Utilidad: Usa Minimax (Profundidad 1) para maximizar su ventaja."""
    nombre = "Minimax (Táctico)"
    
    def __init__(self, semilla=None):
        self.rng = random.Random(semilla)
        self.nodos_expandidos = 0
        
    def evaluar_estado(self, pos, mapa, rivales, bombas):
        # Función de Utilidad:
        # +100 por estar cerca del rival
        # -1000 por estar cerca de una bomba
        # +10 por estar cerca de un bloque rompible
        puntaje = 0
        
        # Riesgo de bombas
        riesgo = any((abs(b[0]-pos[0]) + abs(b[1]-pos[1])) <= 2 for b in bombas)
        if riesgo:
            puntaje -= 1000
            
        if rivales:
            dist_rival = min(abs(r["pos"][0]-pos[0]) + abs(r["pos"][1]-pos[1]) for r in rivales)
            puntaje += (50 - dist_rival * 5)
            
        return puntaje

    def decidir(self, estado, mi_id):
        self.nodos_expandidos = 0
        pos = estado["mi_pos"]
        mapa = estado["mapa"]
        rivales = estado["rivales"]
        bombas = [b["pos"] for b in estado["bombas"]]
        
        mejores_acciones = []
        max_utilidad = -999999
        
        # Simulamos profundidad 1
        posibles = list(DIRS.items()) + [("quieto", (0,0)), ("bomba", (0,0))]
        
        for accion, (df, dc) in posibles:
            self.nodos_expandidos += 1
            nf, nc = pos[0] + df, pos[1] + dc
            
            # Verificamos validez del movimiento
            if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
                if accion == "bomba" or mapa[nf][nc] == VACIO:
                    # Simular estado futuro (simplificado)
                    futuras_bombas = bombas + [(nf, nc)] if accion == "bomba" else bombas
                    
                    utilidad = self.evaluar_estado((nf, nc), mapa, rivales, futuras_bombas)
                    
                    if utilidad > max_utilidad:
                        max_utilidad = utilidad
                        mejores_acciones = [accion]
                    elif utilidad == max_utilidad:
                        mejores_acciones.append(accion)
                        
        if mejores_acciones:
            return self.rng.choice(mejores_acciones)
        return "quieto"

# Registro: la app y los experimentos eligen agentes por nombre
AGENTES = {
    "Aleatorio": AgenteAleatorio,
    "Reflejo (Evasivo)": AgenteReflejo,
    "A* (Cazador)": AgenteAEstrella,
    "Minimax (Táctico)": AgenteMinimax
}
