"""
app.py -- Interfaz Táctica Avanzada de Bomberman IA.
Ejecución: streamlit run app.py (o directamente mediante el botón Run de Python).
"""
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import streamlit.runtime

# Permite ejecutar tanto con "streamlit run app.py" como directamente con el botón Run (python app.py)
if __name__ == "__main__" and not streamlit.runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

from bomberman_env import Entorno, MURO, BLOQUE
from agentes import AGENTES

CELDA = 50
_teclado = components.declare_component("teclado", path=str(Path(__file__).parent / "componente_teclado"))

COLORES = ["#00f2fe", "#f43f5e", "#a3e635", "#f59e0b"]  # Cyan Neón, Carmesí, Lima Ácido, Ámbar

TEMAS = {
    "Cyber Tokio": dict(
        fondo="#020617",
        p1="#081026",
        p2="#0d1733",
        m_base1="#1e293b",
        m_base2="#0f172a",
        m_top1="#334155",
        m_top2="#1e293b",
        m_glow="#38bdf8",
        b_c1="#b45309",
        b_c2="#78350f",
        b_accent="#f59e0b",
        marco="#38bdf8",
    ),
    "Hiperespacio": dict(
        fondo="#050510",
        p1="#0c0c24",
        p2="#121235",
        m_base1="#2e1065",
        m_base2="#17073b",
        m_top1="#581c87",
        m_top2="#2e1065",
        m_glow="#c084fc",
        b_c1="#9d174d",
        b_c2="#700936",
        b_accent="#ec4899",
        marco="#c084fc",
    ),
    "Búnker Táctico": dict(
        fondo="#050d0a",
        p1="#061f14",
        p2="#09281a",
        m_base1="#134e4a",
        m_base2="#042f2e",
        m_top1="#115e59",
        m_top2="#134e4a",
        m_glow="#34d399",
        b_c1="#d97706",
        b_c2="#92400e",
        b_accent="#fbbf24",
        marco="#34d399",
    ),
}


# ==============================================================================
# RENDERIZADO VECTORIAL AVANZADO (SVG)
# ==============================================================================

def _sprite_jugador(cx, cy, color, p_id):
    """Agente táctico con exo-armadura, reactor trasero, hombreras y visor holográfico."""
    glow_id = f"glow-p{p_id}"
    return (
        f'<g class="jugador-operativo">'
        # Sombra de contacto
        f'<ellipse cx="{cx}" cy="{cy + 17}" rx="17" ry="6" fill="#000000" opacity="0.6" filter="url(#f-blur)"/>'
        # Mochila / Reactor dorsal
        f'<rect x="{cx - 10}" y="{cy - 18}" width="20" height="8" rx="3" fill="#090d16" stroke="{color}" stroke-width="1.2"/>'
        f'<circle cx="{cx - 5}" cy="{cy - 14}" r="2" fill="{color}"/>'
        f'<circle cx="{cx + 5}" cy="{cy - 14}" r="2" fill="{color}"/>'
        # Hombreras blindadas
        f'<rect x="{cx - 18}" y="{cy - 4}" width="9" height="13" rx="3" fill="#1e293b" stroke="{color}" stroke-width="1.4"/>'
        f'<rect x="{cx + 9}" y="{cy - 4}" width="9" height="13" rx="3" fill="#1e293b" stroke="{color}" stroke-width="1.4"/>'
        # Coraza pectoral
        f'<path d="M{cx - 11} {cy - 6} L{cx + 11} {cy - 6} L{cx + 8} {cy + 13} L{cx - 8} {cy + 13} Z" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>'
        f'<path d="M{cx - 6} {cy - 2} L{cx + 6} {cy - 2} L{cx + 4} {cy + 9} L{cx - 4} {cy + 9} Z" fill="{color}" opacity="0.85"/>'
        # Casco táctico
        f'<ellipse cx="{cx}" cy="{cy - 8}" rx="12" ry="12" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>'
        # Visor curvo luminoso
        f'<path d="M{cx - 9} {cy - 8} Q{cx} {cy - 3} {cx + 9} {cy - 8} Q{cx} {cy - 13} {cx - 9} {cy - 8}" fill="{color}" filter="url(#{glow_id})"/>'
        # Reflejo especular en visor
        f'<path d="M{cx - 7} {cy - 10} Q{cx - 1} {cy - 12} {cx + 4} {cy - 10}" stroke="#ffffff" stroke-width="1.4" fill="none" opacity="0.85" stroke-linecap="round"/>'
        # Cresta / Insignia operativa
        f'<polygon points="{cx - 3},{cy - 16} {cx + 3},{cy - 16} {cx},{cy - 12}" fill="{color}"/>'
        f'</g>'
    )


def _sprite_bomba(cx, cy, timer):
    """Carga de pulso de plasma con anillo magnético, núcleo LED y chispa energética."""
    return (
        f'<g class="bomba-tactica">'
        # Halo térmico ambiental
        f'<circle cx="{cx}" cy="{cy}" r="22" fill="rgba(244,63,94,0.22)" class="bomba-halo"/>'
        # Sombra profunda
        f'<ellipse cx="{cx}" cy="{cy + 15}" rx="15" ry="5" fill="#000000" opacity="0.75" filter="url(#f-blur)"/>'
        # Esfera de alta densidad con gradiente esférico
        f'<circle cx="{cx}" cy="{cy}" r="15" fill="url(#bomba-body)" stroke="#090d16" stroke-width="1.5"/>'
        # Brillo especular superior
        f'<ellipse cx="{cx - 5}" cy="{cy - 6}" rx="5" ry="2.5" fill="#ffffff" opacity="0.4" transform="rotate(-30 {cx-5} {cy-6})"/>'
        # Abrazadera magnética ecuatorial
        f'<rect x="{cx - 15}" y="{cy - 3}" width="30" height="6" rx="2" fill="#334155" stroke="#475569" stroke-width="0.8"/>'
        f'<circle cx="{cx - 10}" cy="{cy}" r="1" fill="#94a3b8"/><circle cx="{cx + 10}" cy="{cy}" r="1" fill="#94a3b8"/>'
        # Núcleo pulsante digital
        f'<circle cx="{cx}" cy="{cy}" r="6" fill="#030712"/>'
        f'<circle cx="{cx}" cy="{cy}" r="4" fill="#f43f5e" class="bomba-core"/>'
        f'<text x="{cx}" y="{cy + 3}" font-family="Rajdhani, monospace" font-size="9" font-weight="800" fill="#ffffff" text-anchor="middle">{timer}</text>'
        # Detonador y chispa eléctrica
        f'<path d="M{cx + 5} {cy - 11} Q{cx + 12} {cy - 17} {cx + 15} {cy - 13}" stroke="#d6a86a" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        f'<circle cx="{cx + 15}" cy="{cy - 13}" r="4" fill="#fde047" class="bomba-chispa"/>'
        f'</g>'
    )


def _sprite_fuego(cx, cy):
    """Onda de choque de plasma multicapa con destello cegador y partículas."""
    return (
        f'<g class="fuego-plasma">'
        # Halo térmico radial
        f'<circle cx="{cx}" cy="{cy}" r="24" fill="url(#f-plasma)" class="fuego-radial"/>'
        # Anillo de onda de choque
        f'<circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="#fef08a" stroke-width="2.5" class="shockwave"/>'
        # Destello central blanco incandescente
        f'<circle cx="{cx}" cy="{cy}" r="10" fill="#ffffff" opacity="0.9" filter="url(#f-blur)"/>'
        # Rayos de dispersión de plasma
        f'<line x1="{cx - 18}" y1="{cy}" x2="{cx + 18}" y2="{cy}" stroke="#ffffff" stroke-width="2" opacity="0.75"/>'
        f'<line x1="{cx}" y1="{cy - 18}" x2="{cx}" y2="{cy + 18}" stroke="#ffffff" stroke-width="2" opacity="0.75"/>'
        f'</g>'
    )


def _sprite_muro(x, y, t):
    """Monolito de aleación reforzada biselada con micro-circuito luminoso central."""
    w = CELDA - 4
    cx, cy = x + CELDA // 2, y + CELDA // 2
    return (
        f'<g>'
        # Sombra arrojada
        f'<rect x="{x + 4}" y="{y + 6}" width="{w}" height="{w}" rx="8" fill="#000000" opacity="0.5" filter="url(#f-blur)"/>'
        # Bisel exterior
        f'<rect x="{x + 2}" y="{y + 2}" width="{w}" height="{w}" rx="8" fill="url(#m-bevel)" stroke="#090d16" stroke-width="1"/>'
        # Placa superior maquinada
        f'<rect x="{x + 6}" y="{y + 6}" width="{CELDA - 12}" height="{CELDA - 12}" rx="5" fill="url(#m-top)"/>'
        # Borde especular superior/izquierdo
        f'<path d="M{x + 7} {y + CELDA - 7} L{x + 7} {y + 7} L{x + CELDA - 7} {y + 7}" stroke="rgba(255,255,255,0.22)" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
        # Cavidad táctica central con circuito de neón
        f'<rect x="{cx - 6}" y="{cy - 6}" width="12" height="12" rx="3" fill="#020617" stroke="{t["m_glow"]}" stroke-width="1.2"/>'
        f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{t["m_glow"]}"/>'
        f'<line x1="{x + 10}" y1="{cy}" x2="{cx - 6}" y2="{cy}" stroke="{t["m_glow"]}" stroke-width="1" opacity="0.5"/>'
        f'<line x1="{cx + 6}" y1="{cy}" x2="{x + CELDA - 10}" y2="{cy}" stroke="{t["m_glow"]}" stroke-width="1" opacity="0.5"/>'
        f'</g>'
    )


def _sprite_bloque(x, y, t):
    """Contenedor de suministros destructible con franjas de peligro y núcleo de energía."""
    w = CELDA - 6
    cx, cy = x + CELDA // 2, y + CELDA // 2
    return (
        f'<g>'
        # Sombra
        f'<rect x="{x + 4}" y="{y + 6}" width="{w}" height="{w}" rx="6" fill="#000000" opacity="0.45" filter="url(#f-blur)"/>'
        # Estructura del contenedor
        f'<rect x="{x + 3}" y="{y + 3}" width="{w}" height="{w}" rx="6" fill="url(#b-base)" stroke="#000000" stroke-width="1"/>'
        # Franjas diagonales de advertencia táctica
        f'<rect x="{x + 7}" y="{y + 7}" width="{CELDA - 14}" height="{CELDA - 14}" rx="4" fill="url(#hazard-pattern)"/>'
        # Cantoneras de refuerzo en esquinas
        f'<rect x="{x + 3}" y="{y + 3}" width="7" height="7" fill="#334155" rx="1"/>'
        f'<rect x="{x + CELDA - 10}" y="{y + 3}" width="7" height="7" fill="#334155" rx="1"/>'
        f'<rect x="{x + 3}" y="{y + CELDA - 10}" width="7" height="7" fill="#334155" rx="1"/>'
        f'<rect x="{x + CELDA - 10}" y="{y + CELDA - 10}" width="7" height="7" fill="#334155" rx="1"/>'
        # Barra luminosa indicadora de energía
        f'<rect x="{cx - 10}" y="{cy - 2}" width="20" height="4" rx="2" fill="{t["b_accent"]}" stroke="#000" stroke-width="0.5"/>'
        f'</g>'
    )


def dibujar_tablero(env, fuego, tema):
    t, n = TEMAS[tema], env.tamano
    w = n * CELDA

    # Definiciones de filtros, patrones y gradientes de alta fidelidad
    defs = [
        '<defs>',
        # Filtro de desenfoque para sombras suaves
        '<filter id="f-blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>',
        # Filtros de resplandor Neón
        '<filter id="glow-p0" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<filter id="glow-p1" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<filter id="glow-p2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<filter id="glow-p3" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        # Patrón de peligro táctico (Hazard stripes)
        '<pattern id="hazard-pattern" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="5" height="10" fill="{t["b_c1"]}"/>'
        f'<rect x="5" width="5" height="10" fill="{t["b_c2"]}"/>'
        '</pattern>',
        # Gradientes para Muros
        f'<linearGradient id="m-bevel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["m_base1"]}"/><stop offset="1" stop-color="{t["m_base2"]}"/></linearGradient>',
        f'<linearGradient id="m-top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["m_top1"]}"/><stop offset="1" stop-color="{t["m_top2"]}"/></linearGradient>',
        # Gradientes para Bloques destructibles
        f'<linearGradient id="b-base" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["b_c1"]}"/><stop offset="1" stop-color="{t["b_c2"]}"/></linearGradient>',
        # Gradiente esférico para la bomba
        '<radialGradient id="bomba-body" cx="35%" cy="30%" r="70%">'
        '<stop offset="0%" stop-color="#334155"/>'
        '<stop offset="35%" stop-color="#1e293b"/>'
        '<stop offset="85%" stop-color="#090d16"/>'
        '<stop offset="100%" stop-color="#000000"/>'
        '</radialGradient>',
        # Gradiente radial de plasma explosivo
        '<radialGradient id="f-plasma" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#ffffff"/>'
        '<stop offset="30%" stop-color="#fef08a"/>'
        '<stop offset="65%" stop-color="#f97316"/>'
        '<stop offset="90%" stop-color="#dc2626"/>'
        '<stop offset="100%" stop-color="rgba(220,38,38,0)"/>'
        '</radialGradient>',
        '</defs>'
    ]

    elementos = [''.join(defs)]

    # 1. Dibujar suelo cuadriculado de alta tecnología
    for f in range(n):
        for c in range(n):
            x, y = c * CELDA, f * CELDA
            color_suelo = t["p1"] if (f + c) % 2 == 0 else t["p2"]
            elementos.append(f'<rect x="{x}" y="{y}" width="{CELDA}" height="{CELDA}" fill="{color_suelo}"/>')
            # Micro-marcas tácticas en las esquinas de cada cuadrícula
            elementos.append(f'<circle cx="{x}" cy="{y}" r="1" fill="#ffffff" opacity="0.12"/>')

            tipo = env.mapa[f][c]
            if tipo == MURO:
                elementos.append(_sprite_muro(x, y, t))
            elif tipo == BLOQUE:
                elementos.append(_sprite_bloque(x, y, t))

            # Fuego activo en la celda
            if (f, c) in fuego:
                elementos.append(_sprite_fuego(x + CELDA // 2, y + CELDA // 2))

    # 2. Dibujar bombas activas
    for b in env.bombas:
        elementos.append(_sprite_bomba(b.pos[1] * CELDA + CELDA // 2, b.pos[0] * CELDA + CELDA // 2, b.timer))

    # 3. Dibujar participantes vivos
    for p in env.participantes:
        if p.vivo:
            color = COLORES[p.id % len(COLORES)]
            elementos.append(_sprite_jugador(p.pos[1] * CELDA + CELDA // 2, p.pos[0] * CELDA + CELDA // 2, color, p.id))

    # Marco exterior táctico
    marco = (
        f'<rect x="-8" y="-8" width="{w + 16}" height="{w + 16}" rx="14" fill="none" stroke="{t["m_base1"]}" stroke-width="16"/>'
        f'<rect x="-16" y="-16" width="{w + 32}" height="{w + 32}" rx="18" fill="none" stroke="{t["marco"]}" stroke-width="1.5" opacity="0.4"/>'
        # Esquinas decorativas iluminadas
        f'<path d="M -10 -2 L -10 -10 L -2 -10" stroke="{t["marco"]}" stroke-width="3" fill="none"/>'
        f'<path d="M {w+2} -10 L {w+10} -10 L {w+10} -2" stroke="{t["marco"]}" stroke-width="3" fill="none"/>'
        f'<path d="M -10 {w+2} L -10 {w+10} L -2 {w+10}" stroke="{t["marco"]}" stroke-width="3" fill="none"/>'
        f'<path d="M {w+2} {w+10} L {w+10} {w+10} L {w+10} {w+2}" stroke="{t["marco"]}" stroke-width="3" fill="none"/>'
    )

    css = (
        "body{margin:0;background:transparent}"
        "svg{border-radius:18px;max-width:100%;height:auto;display:block;box-shadow:0 25px 60px rgba(0,0,0,0.85)}"
        ".jugador-operativo{animation:hoverOp 1.8s ease-in-out infinite alternate;transform-origin:center;transform-box:fill-box}"
        "@keyframes hoverOp{from{transform:translateY(0px)}to{transform:translateY(-1.8px)}}"
        ".bomba-tactica{animation:pulseBomba .55s infinite alternate;transform-origin:center;transform-box:fill-box}"
        "@keyframes pulseBomba{to{transform:scale(1.08)}}"
        ".bomba-chispa{animation:chispaSpark .18s infinite alternate}"
        "@keyframes chispaSpark{to{opacity:.35;transform:scale(1.3)}}"
        ".fuego-plasma{animation:fuegoExp .4s cubic-bezier(0.16,1,0.3,1);transform-origin:center;transform-box:fill-box}"
        "@keyframes fuegoExp{from{transform:scale(.3);opacity:0}to{transform:scale(1);opacity:1}}"
        ".shockwave{animation:shockRing .4s ease-out;transform-origin:center;transform-box:fill-box}"
        "@keyframes shockRing{from{r:10;opacity:1}to{r:26;opacity:0}}"
    )

    return f'<style>{css}</style><svg viewBox="-16 -16 {w + 32} {w + 32}" width="{w + 32}">{"".join(elementos)}{marco}</svg>'


# ==============================================================================
# LÓGICA DE PARTIDA
# ==============================================================================

def nueva_partida():
    ss = st.session_state
    nombres = [ss.get("puesto0", "Humano"), ss.get("puesto1", list(AGENTES)[0])]
    env = Entorno(tamano=ss.get("tamano", 11), alcance=ss.get("alcance", 2), semilla=ss.get("semilla", 0))
    env.reiniciar(nombres, rotacion=ss.get("rotacion", 0))
    ss.env = env
    ss.agentes = {i: AGENTES[n](ss.get("semilla", 0) * 100 + i) for i, n in enumerate(nombres) if n != "Humano"}
    ss.fuego = set()
    ss.pausado = False


def alternar_pausa():
    st.session_state.pausado = not st.session_state.pausado


def jugar_turno(accion_humana="quieto"):
    ss, env = st.session_state, st.session_state.env
    if env.terminado:
        return
    acciones = {}
    for p in env.vivos():
        if p.nombre == "Humano":
            acciones[p.id] = accion_humana
        else:
            estado = env.percibir(p.id)
            acciones[p.id] = ss.agentes[p.id].decidir(estado, p.id)
    ss.fuego = set()
    for b in env.bombas:
        if b.timer == 1:
            ss.fuego |= env._celdas_explosion(b)[0]
    env.paso(acciones)


# ==============================================================================
# INTERFAZ STREAMLIT DE ALTA FIDELIDAD
# ==============================================================================

st.set_page_config(page_title="Bomberman Tactical IA", layout="wide", initial_sidebar_state="expanded")

# Inyección de estilos CSS futuristas con fuentes modernas (Rajdhani & Outfit)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap');

/* Fondo General con Gradiente Cyberpunk */
.stApp {
    background: radial-gradient(circle at 15% 10%, #0d1527, #020617 80%) !important;
    font-family: 'Outfit', -apple-system, sans-serif !important;
    color: #e2e8f0;
}

/* Ocultar elementos estándar de Streamlit */
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }

/* Barra Superior / Brand */
.top-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 16px;
}
.brand-box {
    display: flex;
    align-items: center;
    gap: 14px;
}
.brand-icon {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(139, 92, 246, 0.2));
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
}
.brand-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: 2px;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin: 0;
}
.brand-sub {
    font-size: 0.8rem;
    color: #94a3b8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 600;
}
.telemetry-tag {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 14px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 20px;
    font-family: 'Rajdhani', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: #38bdf8;
    letter-spacing: 1px;
}

/* Tarjetas de Operativos (HUD Derecho) */
.hud-panel {
    background: rgba(15, 23, 42, 0.55);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}
.hud-panel-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.op-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-radius: 12px;
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.06);
    transition: all 0.25s ease;
}
.op-card:hover {
    background: rgba(30, 41, 59, 0.7);
    border-color: rgba(255, 255, 255, 0.15);
}
.op-card.p0 { border-left: 4px solid #00f2fe; }
.op-card.p1 { border-left: 4px solid #f43f5e; }

.op-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.op-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 1px;
    color: #f8fafc;
}
.op-role {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.badge-live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #10b981;
}
.badge-dead {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1px;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #ef4444;
}
.pulse-beacon {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 8px currentColor;
}

/* Banner de Victoria / Fin */
.banner-victory {
    padding: 16px;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 14px;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(244, 63, 94, 0.2));
    border: 1px solid rgba(245, 158, 11, 0.5);
    box-shadow: 0 0 25px rgba(245, 158, 11, 0.25);
}
.banner-victory-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #fef08a;
    margin: 0;
}
.banner-victory-sub {
    font-size: 0.8rem;
    color: #cbd5e1;
    margin-top: 4px;
    letter-spacing: 1px;
}

/* Barra de progreso de turnos */
.progress-container {
    margin-top: 10px;
}
.progress-label {
    display: flex;
    justify-content: space-between;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #94a3b8;
    margin-bottom: 4px;
}
.progress-bar-bg {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    overflow: hidden;
}
.progress-bar-val {
    height: 100%;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    border-radius: 10px;
    transition: width 0.3s ease;
}

/* Estilización de Botones */
div.stButton > button {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 10px 16px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
}
div.stButton > button:hover {
    border-color: #38bdf8 !important;
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(129, 140, 248, 0.2)) !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* Personalización de la Barra Lateral */
[data-testid="stSidebar"] {
    background: #030712 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.sidebar-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #38bdf8;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(56, 189, 248, 0.2);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
""", unsafe_allow_html=True)


# Barra Lateral: Controles y Configuración
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line>
            <line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line>
            <line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line>
        </svg>
        CONFIGURACIÓN TÁCTICA
    </div>
    """, unsafe_allow_html=True)

    st.selectbox("Modo de Juego", ["1 vs 1"], key="modo")
    st.selectbox("Operativo 01", ["Humano"] + list(AGENTES), key="puesto0")
    st.selectbox("Rival Táctico", list(AGENTES), key="puesto1")
    st.number_input("Semilla de Generación", 0, 9999, 0, key="semilla")
    st.slider("Dimensión de la Arena (impar)", 7, 15, 11, 2, key="tamano")
    st.slider("Radio de Explosión de Bomba", 1, 5, 2, key="alcance")
    st.selectbox("Rotación de Esquinas", [0, 1, 2, 3], key="rotacion")
    st.selectbox("Estilo Visual de la Arena", list(TEMAS), key="tema")
    st.slider("Velocidad de Simulación (ms)", 150, 700, 350, 50, key="tick")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.button("REINICIAR SIMULACIÓN", on_click=nueva_partida, use_container_width=True)

# Inicialización segura
if "env" not in st.session_state:
    nueva_partida()
env, ss = st.session_state.env, st.session_state

# Cabecera Principal de la Aplicación
st.markdown("""
<div class="top-header">
    <div class="brand-box">
        <div class="brand-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="9"></circle>
                <line x1="12" y1="3" x2="12" y2="7"></line>
                <line x1="12" y1="17" x2="12" y2="21"></line>
                <line x1="3" y1="12" x2="7" y2="12"></line>
                <line x1="17" y1="12" x2="21" y2="12"></line>
            </svg>
        </div>
        <div>
            <div class="brand-title">NEO BOMBERMAN</div>
            <div class="brand-sub">TACTICAL IA ARENA · MOTOR DINÁMICO</div>
        </div>
    </div>
    <div class="telemetry-tag">
        <span class="pulse-beacon"></span>
        ESTADO: SIMULACIÓN EN TIEMPO REAL
    </div>
</div>
""", unsafe_allow_html=True)

# Procesamiento del tick del reloj desde el iframe
v = ss.get("juego")
if v and (v["sesion"], v["n"]) != ss.get("visto") and not ss.pausado:
    ss.visto = (v["sesion"], v["n"])
    jugar_turno(v["tecla"] or "quieto")

# Distribución del Tablero y Panel de Control
col_tablero, col_hud = st.columns([3, 1.4])

with col_tablero:
    _teclado(
        svg=dibujar_tablero(env, ss.fuego, ss.get("tema", "Cyber Tokio")),
        activo=(not env.terminado and not ss.pausado),
        tick_ms=ss.get("tick", 350),
        turno=env.turno,
        alto=(env.tamano * CELDA + 40),
        mensaje="SIMULACIÓN PAUSADA" if ss.pausado else "CONTROLES: FLECHAS O WASD · ESPACIO: DESPLEGAR CARGA",
        key="juego",
        default=None,
    )

with col_hud:
    # 1. Cartel de Estado Final si terminó la partida
    if env.terminado:
        if env.ganador_equipo is None:
            titulo_res = "EMPATE TÁCTICO" if env.motivo_fin == "empate" else "LÍMITE TEMPORAL AGOTADO"
            sub_res = "Ambos agentes cayeron en combate o se agotaron los turnos."
        else:
            ganador = env.participantes[env.ganador_equipo].nombre
            titulo_res = f"VICTORIA: {ganador.upper()}"
            sub_res = "Objetivo neutralizado con éxito en la arena."

        st.markdown(f"""
        <div class="banner-victory">
            <div class="banner-victory-title">{titulo_res}</div>
            <div class="banner-victory-sub">{sub_res}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Panel de Operativos Activos
    st.markdown("""
    <div class="hud-panel">
        <div class="hud-panel-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            ESTADO DE OPERATIVOS
        </div>
    """, unsafe_allow_html=True)

    for p in env.participantes:
        clase_p = f"p{p.id}"
        rol = "HUMANO (PILOTO)" if p.nombre == "Humano" else f"NÚCLEO IA · {p.nombre.upper()}"
        if p.vivo:
            badge_html = '<span class="badge-live"><span class="pulse-beacon"></span>OPERATIVO</span>'
        else:
            badge_html = '<span class="badge-dead"><span class="pulse-beacon"></span>ELIMINADO</span>'

        st.markdown(f"""
        <div class="op-card {clase_p}">
            <div class="op-info">
                <div class="op-name">{p.nombre} (P{p.id})</div>
                <div class="op-role">{rol} · Bajas: {p.eliminaciones}</div>
            </div>
            <div>{badge_html}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Telemetría de Combate
    porcentaje = int((env.turno / max(1, env.max_turnos)) * 100)
    st.markdown(f"""
    <div class="hud-panel">
        <div class="hud-panel-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            CRONOMETRÍA Y TELEMETRÍA
        </div>
        <div class="progress-container">
            <div class="progress-label">
                <span>CICLO DE SIMULACIÓN</span>
                <span>{env.turno} / {env.max_turnos}</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-val" style="width: {min(100, porcentaje)}%;"></div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 14px; font-size: 0.8rem; color: #64748b; font-family: 'Rajdhani', monospace;">
            <span>ARENA: {env.tamano}x{env.tamano}</span>
            <span>BOMBAS: {len(env.bombas)}</span>
            <span>RADIO: {env.alcance}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón de Pausa / Reanudación
    texto_pausa = "REANUDAR SIMULACIÓN" if ss.pausado else "PAUSAR SIMULACIÓN"
    st.button(texto_pausa, on_click=alternar_pausa, use_container_width=True)
