"""
experimentos.py -- Corre partidas y devuelve un DataFrame con la tabla comparativa.

Uso:
    python experimentos.py          # imprime la tabla (Aleatorio vs Aleatorio, 1v1, 30 partidas)
    python experimentos.py --ver    # además muestra una partida paso a paso en texto
"""
import sys
import time
import pandas as pd

from bomberman_env import Entorno
from agentes import AGENTES


def jugar_partida(nombres_agentes, semilla, rotacion=0, mostrar=False, **params):
    """Juega UNA partida solo con agentes. Devuelve (resumen, ms_decision_por_id)."""
    env = Entorno(semilla=semilla, **params)
    env.reiniciar(nombres_agentes, rotacion=rotacion)
    agentes = {i: AGENTES[nombre](semilla * 100 + i)       # semilla propia por agente
               for i, nombre in enumerate(nombres_agentes)}
    tiempos = {i: [] for i in agentes}

    while not env.terminado:
        acciones = {}
        for p in env.vivos():
            estado = env.percibir(p.id)                    # <-- AQUÍ el agente PERCIBE
            t0 = time.perf_counter()
            acciones[p.id] = agentes[p.id].decidir(estado, p.id)   # DECIDE
            tiempos[p.id].append((time.perf_counter() - t0) * 1000)
        env.paso(acciones)                                 # <-- AQUÍ el agente ACTÚA
        if mostrar:
            print(f"\nTurno {env.turno}\n{env.dibujar()}")

    return env.resumen(), tiempos


def correr_comparacion(nombres_agentes, n_partidas=30, **params):
    """Juega n_partidas con semillas 0..n-1 y rotando esquinas. Una fila por participante."""
    filas = []
    for k in range(n_partidas):
        resumen, tiempos = jugar_partida(nombres_agentes, semilla=k, rotacion=k % 4, **params)
        for p in resumen["participantes"]:
            ms = tiempos[p["id"]]
            filas.append({
                "tecnica": p["nombre"],
                "partida": k,
                "gano": int(p["equipo"] == resumen["ganador_equipo"]),
                "empate": int(resumen["ganador_equipo"] is None),
                "eliminaciones": p["eliminaciones"],
                "autoeliminado": int(p["autoeliminado"]),
                "turnos_vivo": p["turnos_vivo"],
                "ms_decision": sum(ms) / len(ms) if ms else 0.0,
            })
    return pd.DataFrame(filas)


def tabla_comparativa(df):
    """Agrupa por técnica con pandas."""
    g = df.groupby("tecnica")
    tabla = pd.DataFrame({
        "% victorias": g["gano"].mean() * 100,
        "Tiempo (ms/decisión)": g["ms_decision"].mean(),
        "Corridas": g["partida"].nunique(),
        "Rivales eliminados": g["eliminaciones"].mean(),
        "% autoeliminación": g["autoeliminado"].mean() * 100,
        "Turnos sobrevividos": g["turnos_vivo"].mean(),
        "Desv. estándar (victoria, %)": g["gano"].std() * 100,
    })
    return tabla.round(3).reset_index().rename(columns={"tecnica": "Técnica"})


if __name__ == "__main__":
    if "--ver" in sys.argv:
        jugar_partida(["Aleatorio", "Aleatorio"], semilla=0, mostrar=True)

    df = correr_comparacion(["Aleatorio", "Aleatorio"], n_partidas=30)
    print("\n=== Aleatorio vs Aleatorio (1v1, 30 partidas) ===")
    print(tabla_comparativa(df).to_string(index=False))
    n_empates = int(df.groupby("partida")["empate"].first().sum())
    print(f"\nEmpates (nadie gana): {n_empates} de 30 partidas")
