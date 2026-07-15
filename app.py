import streamlit as st
#st.title("Hello, Streamlit!")
#st.write("Si ves esto, Streamlit funciona correctamente 🎉")

#app.py
#"""
Interfaz Streamlit para el agente de soporte BimBam Buy.
#"""

import os
import time
import requests
import threading
import streamlit as st
from dotenv import load_dotenv

from src.rag_chain import BimBamBuyAgent

load_dotenv()

OCI_LOG_ENDPOINT = os.getenv("OCI_LOG_ENDPOINT")

st.set_page_config(
    page_title="BimBam Buy Support",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Estilos personalizados — paleta azul/morado
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    :root {
        --bb-primary: #6C5CE7;
        --bb-secondary: #4F8EF7;
        --bb-gradient: linear-gradient(135deg, #6C5CE7 0%, #4F8EF7 100%);
        --bb-bg-soft: rgba(108, 92, 231, 0.08);
    }

    /* Ocultar el menú por defecto y el footer "Made with Streamlit" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Banner superior con gradiente */
    .bb-header {
        background: var(--bb-gradient);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(108, 92, 231, 0.25);
    }
    .bb-header h1 {
        color: white;
        font-size: 1.9rem;
        margin: 0 0 0.4rem 0;
        font-weight: 700;
    }
    .bb-header p {
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-size: 0.95rem;
    }

    /* Burbujas de chat */
    div[data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 0.4rem 0.2rem;
    }

    /* Badges de fuentes */
    .bb-source-badge {
        display: inline-block;
        background: var(--bb-bg-soft);
        color: var(--bb-secondary);
        border: 1px solid rgba(108, 92, 231, 0.3);
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        font-size: 0.78rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
    }

    /* Botones de preguntas sugeridas */
    .stButton > button {
        border-radius: 999px;
        border: 1px solid rgba(108, 92, 231, 0.35);
        background: var(--bb-bg-soft);
        color: var(--bb-primary);
        font-size: 0.82rem;
        padding: 0.35rem 0.9rem;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: var(--bb-gradient);
        color: white;
        border-color: transparent;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(108, 92, 231, 0.15);
    }
</style>
""", unsafe_allow_html=True)

EXAMPLE_QUESTIONS = [
    "¿Cómo solicito un reembolso?",
    "¿Qué métodos de pago aceptan?",
    "¿Cuánto tarda un envío?",
    "¿Qué cubre la garantía?",
]


def log_to_oracle(pregunta, respuesta, fuentes, tiempo_ms):
    """Registra la ejecución en Oracle Autonomous DB vía ORDS (servicio OCI).
    Se ejecuta en un hilo aparte para no bloquear la interfaz si Oracle tarda."""
    if not OCI_LOG_ENDPOINT:
        return

    def _send():
        try:
            requests.post(
                OCI_LOG_ENDPOINT,
                json={
                    "pregunta": pregunta,
                    "respuesta": respuesta,
                    "fuentes": ", ".join(fuentes) if fuentes else "",
                    "tiempo_ms": tiempo_ms,
                },
                timeout=30,
            )
        except requests.RequestException as e:
            print(f"[warn] No se pudo registrar en Oracle: {e}")

    threading.Thread(target=_send, daemon=True).start()


@st.cache_resource(show_spinner=False)
def load_agent():
    """Carga el agente una sola vez por sesión de servidor."""
    return BimBamBuyAgent()


def render_sources(sources):
    if not sources:
        return
    badges = "".join(f'<span class="bb-source-badge">📄 {s}</span>' for s in sources)
    st.markdown(badges, unsafe_allow_html=True)


def handle_question(question, agent):
    """Procesa una pregunta (venga del chat_input o de un botón sugerido)."""
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🙋"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="💬"):
        with st.spinner("Buscando en la documentación..."):
            result = agent.ask(question)

        answer = result["answer"]
        sources = result["sources"]

        st.markdown(answer)
        render_sources(sources)
        st.caption(f"⏱️ Respondido en {result['elapsed_ms']} ms")

        log_to_oracle(
            pregunta=question,
            respuesta=answer,
            fuentes=sources,
            tiempo_ms=result["elapsed_ms"],
        )

    st.session_state.messages.append({"role": "assistant", "content": answer})


def main():
    st.markdown("""
    <div class="bb-header">
        <h1>💬 BimBam Buy Support</h1>
        <p>Tu asistente de atención al cliente, disponible 24/7</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Cargando agente..."):
        try:
            agent = load_agent()
        except Exception as e:
            st.error(f"No se pudo inicializar el agente: {e}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Preguntas sugeridas solo si aún no hay conversación
    if not st.session_state.messages:
        st.caption("Prueba con una de estas preguntas:")
        cols = st.columns(2)
        for i, q in enumerate(EXAMPLE_QUESTIONS):
            if cols[i % 2].button(q, key=f"suggested_{i}", use_container_width=True):
                handle_question(q, agent)
                st.rerun()

    # Historial
    for msg in st.session_state.messages:
        avatar = "🙋" if msg["role"] == "user" else "💬"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Input del usuario
    question = st.chat_input("Escribe tu pregunta...")
    if question:
        handle_question(question, agent)

    with st.sidebar:
        st.markdown("### ℹ️ Acerca del agente")
        st.markdown(
            """
            **BimBam Buy Support** es un agente RAG que responde
            preguntas basándose únicamente en la documentación oficial:
            """
        )
        for doc in [
            "Política de Reembolsos y Devoluciones",
            "Guía de Tiempos y Costos de Envío",
            "Manual de Garantía de Productos",
            "Preguntas Frecuentes sobre Métodos de Pago",
            "Programa de Afiliados",
        ]:
            st.markdown(f"- {doc}")

        st.divider()
        if st.button("🗑️ Limpiar conversación", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()