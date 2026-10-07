"""
bomberman_env.py -- Motor del Bomberman simplificado (por turnos).

CICLO DE UN TURNO (esto se puede preguntar en el oral):
  1. PERCIBIR : el entorno le da a cada participante vivo un "estado".
  2. DECIDIR  : cada participante devuelve UNA acción.
  3. ACTUAR   : el entorno resuelve todas las acciones en un orden fijo:
       a) Poner bombas      (en orden de id: 0, 1, 2, 3)
       b) Mover             (en orden de id; si la celda ya está ocupada, no se mueve)
       c) Explotar bombas   (el temporizador baja 1; las que llegan a 0 explotan,
                             y una explosión que toca otra bomba la detona en cadena)
       d) Revisar fin de partida (victoria, empate o límite de turnos)
"""
import random
from dataclasses import dataclass

# ---------- Constantes ----------
VACIO, MURO, BLOQUE = 0, 1, 2

ACCIONES = ["arriba", "abajo", "izquierda", "derecha", "quieto", "poner_bomba"]

# (cambio_fila, cambio_columna) de cada movimiento
MOVIMIENTOS = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}


@dataclass
class Participante:
    id: int
    nombre: str          # nombre del agente (o "Humano")
    equipo: int          # en 1vsN cada uno es su propio equipo
    pos: tuple           # (fila, columna)
    vivo: bool = True
    eliminaciones: int = 0
    autoeliminado: bool = False
    turnos_vivo: int = 0


@dataclass(eq=False)
class Bomba:
    pos: tuple
    dueno: int           # id del participante que la puso
    equipo: int
    timer: int           # turnos que faltan para explotar


class Entorno:
    def __init__(self, tamano=11, alcance=2, semilla=0, max_turnos=150,
                 prob_bloque=0.35, timer_bomba=4, max_bombas=1):
        # El tamaño debe ser impar para que las esquinas no caigan en un muro
        self.tamano = tamano if tamano % 2 == 1 else tamano + 1
        self.alcance = alcance
        self.semilla = semilla
        self.max_turnos = max_turnos
        self.prob_bloque = prob_bloque
        self.timer_bomba = timer_bomba
        self.max_bombas = max_bombas  # bombas activas permitidas por participante

    # ------------------------------------------------------------------
    # Preparación de la partida
    # ------------------------------------------------------------------
    def reiniciar(self, nombres, equipos=None, rotacion=0):
        """Crea mapa y participantes. 'rotacion' mueve las esquinas iniciales."""
        self.rng = random.Random(self.semilla)  # misma semilla = mismo mapa
        self.mapa = self._crear_mapa()
        self.bombas = []
        self.turno = 0
        self.terminado = False
        self.ganador_equipo = None
        self.motivo_fin = ""
        self.bloques_destruidos = 0

        n = self.tamano - 1
        esquinas = [(0, 0), (n, n), (0, n), (n, 0)]   # las 2 primeras son opuestas
        r = rotacion % 4
        esquinas = esquinas[r:] + esquinas[:r]

        if equipos is None:
            equipos = list(range(len(nombres)))        # cada uno su propio equipo
        self.participantes = [
            Participante(id=i, nombre=nombres[i], equipo=equipos[i], pos=esquinas[i])
            for i in range(len(nombres))
        ]

    def _crear_mapa(self):
        n = self.tamano
        mapa = [[VACIO] * n for _ in range(n)]
        for f in range(n):
            for c in range(n):
                if f % 2 == 1 and c % 2 == 1:
                    mapa[f][c] = MURO                       # pilares fijos
                elif not self._cerca_de_esquina(f, c) and self.rng.random() < self.prob_bloque:
                    mapa[f][c] = BLOQUE                     # bloques destructibles
        return mapa

    def _cerca_de_esquina(self, f, c):
        """Deja libre una zona pequeña en cada esquina para poder empezar."""
        n = self.tamano - 1
        for cf, cc in [(0, 0), (0, n), (n, 0), (n, n)]:
            if abs(f - cf) + abs(c - cc) <= 2:
                return True
        return False

    # ------------------------------------------------------------------
    # Consultas auxiliares
    # ------------------------------------------------------------------
    def vivos(self):
        return [p for p in self.participantes if p.vivo]

    def _dentro(self, pos):
        return 0 <= pos[0] < self.tamano and 0 <= pos[1] < self.tamano

    def _puede_entrar(self, pos):
        """Una celda es transitable si está en el mapa, vacía, sin bomba y sin nadie."""
        if not self._dentro(pos):
            return False
        if self.mapa[pos[0]][pos[1]] != VACIO:
            return False
        if any(b.pos == pos for b in self.bombas):
            return False
        if any(p.vivo and p.pos == pos for p in self.participantes):
            return False
        return True

    def _celdas_explosion(self, bomba):
        """Celdas que alcanza una bomba (cruz). Se detiene en muros y en el primer bloque."""
        celdas = {bomba.pos}
        bloques = set()
        for df, dc in MOVIMIENTOS.values():
            for k in range(1, self.alcance + 1):
                celda = (bomba.pos[0] + df * k, bomba.pos[1] + dc * k)
                if not self._dentro(celda):
                    break
                tipo = self.mapa[celda[0]][celda[1]]
                if tipo == MURO:
                    break                      # el muro frena el fuego (no se incluye)
                celdas.add(celda)
                if tipo == BLOQUE:
                    bloques.add(celda)         # el bloque se rompe y frena el fuego
                    break
        return celdas, bloques

    def zona_peligro(self):
        """Todas las celdas que serán alcanzadas por las bombas que hay ahora."""
        peligro = set()
        for b in self.bombas:
            celdas, _ = self._celdas_explosion(b)
            peligro |= celdas
        return peligro

    # ------------------------------------------------------------------
    # 1) PERCIBIR
    # ------------------------------------------------------------------
    def percibir(self, id_participante):
        """Estado que ve un participante (el mismo formato para agentes y humano)."""
        yo = self.participantes[id_participante]
        otros = [p for p in self.participantes if p.id != yo.id and p.vivo]
        return {
            "turno": self.turno,
            "tamano": self.tamano,
            "alcance": self.alcance,
            "mapa": [fila[:] for fila in self.mapa],     # copia: el agente no puede alterar el mapa
            "mi_pos": yo.pos,
            "aliados": [{"id": p.id, "pos": p.pos} for p in otros if p.equipo == yo.equipo],
            "rivales": [{"id": p.id, "pos": p.pos} for p in otros if p.equipo != yo.equipo],
            "bombas": [{"pos": b.pos, "dueno": b.dueno, "equipo": b.equipo, "timer": b.timer}
                       for b in self.bombas],
            "peligro": self.zona_peligro(),
        }

    # ------------------------------------------------------------------
    # 3) ACTUAR
    # ------------------------------------------------------------------
    def paso(self, acciones):
        """Resuelve un turno. 'acciones' es un dict {id_participante: accion}."""
        vivos = self.vivos()                      # ya vienen ordenados por id
        for p in vivos:
            p.turnos_vivo += 1

        self._poner_bombas(vivos, acciones)       # a) bombas
        self._mover(vivos, acciones)              # b) movimientos
        self._explotar()                          # c) temporizadores y explosiones
        self.turno += 1
        self._revisar_fin()                       # d) fin de partida

    def _poner_bombas(self, vivos, acciones):
        for p in vivos:
            if acciones.get(p.id) != "poner_bomba":
                continue
            activas = sum(1 for b in self.bombas if b.dueno == p.id)
            hay_bomba_aqui = any(b.pos == p.pos for b in self.bombas)
            if activas < self.max_bombas and not hay_bomba_aqui:
                self.bombas.append(Bomba(p.pos, p.id, p.equipo, self.timer_bomba))

    def _mover(self, vivos, acciones):
        for p in vivos:
            accion = acciones.get(p.id)
            if accion in MOVIMIENTOS:
                df, dc = MOVIMIENTOS[accion]
                destino = (p.pos[0] + df, p.pos[1] + dc)
                if self._puede_entrar(destino):   # si no puede, se queda quieto
                    p.pos = destino

    def _explotar(self):
        for b in self.bombas:
            b.timer -= 1
        cola = [b for b in self.bombas if b.timer <= 0]
        fuego = {}                 # celda -> set de dueños de las bombas que la alcanzan
        bloques_rotos = set()

        while cola:                # reacción en cadena
            b = cola.pop(0)
            self.bombas.remove(b)
            celdas, bloques = self._celdas_explosion(b)
            bloques_rotos |= bloques
            for celda in celdas:
                fuego.setdefault(celda, set()).add(b.dueno)
            for otra in self.bombas:           # el fuego detona otras bombas
                if otra.pos in celdas and otra not in cola:
                    cola.append(otra)

        for (f, c) in bloques_rotos:           # se rompen al final (el orden no importa)
            self.mapa[f][c] = VACIO
            self.bloques_destruidos += 1

        for p in self.vivos():                 # muertes
            duenos = fuego.get(p.pos)
            if duenos:
                p.vivo = False
                if p.id in duenos:
                    p.autoeliminado = True
                for d in duenos - {p.id}:
                    self.participantes[d].eliminaciones += 1

    def _revisar_fin(self):
        equipos_vivos = {p.equipo for p in self.participantes if p.vivo}
        if len(equipos_vivos) == 1:
            self.terminado = True
            self.ganador_equipo = equipos_vivos.pop()
            self.motivo_fin = "victoria"
        elif len(equipos_vivos) == 0:
            self.terminado = True
            self.motivo_fin = "empate"
        elif self.turno >= self.max_turnos:
            self.terminado = True
            self.motivo_fin = "limite_turnos"

    # ------------------------------------------------------------------
    # Registro y dibujo
    # ------------------------------------------------------------------
    def resumen(self):
        """Datos de la partida para las estadísticas."""
        return {
            "ganador_equipo": self.ganador_equipo,
            "motivo_fin": self.motivo_fin,
            "turnos": self.turno,
            "bloques_destruidos": self.bloques_destruidos,
            "participantes": [
                {"id": p.id, "nombre": p.nombre, "equipo": p.equipo,
                 "eliminaciones": p.eliminaciones,
                 "autoeliminado": p.autoeliminado,
                 "turnos_vivo": p.turnos_vivo}
                for p in self.participantes
            ],
        }

    def dibujar(self):
        """Tablero en texto: ## muro, [] bloque, () bomba, P0/P1 participantes, x0 = muerto."""
        n = self.tamano
        filas = []
        for f in range(n):
            fila = ""
            for c in range(n):
                celda = "  "
                if self.mapa[f][c] == MURO:
                    celda = "##"
                elif self.mapa[f][c] == BLOQUE:
                    celda = "[]"
                if any(b.pos == (f, c) for b in self.bombas):
                    celda = "()"
                for p in self.participantes:
                    if p.vivo and p.pos == (f, c):
                        celda = f"P{p.id}"
                fila += celda
            filas.append(fila)
        return "\n".join(filas)
