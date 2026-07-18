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
    .bb-header {
        position: relative;
    }
    .bb-github-link {
        position: absolute;
        top: 1rem;
        right: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.35);
        border-radius: 999px;
        padding: 0.3rem 0.8rem;
        text-decoration: none;
        font-size: 0.78rem;
        color: white;
        transition: all 0.15s ease;
    }
    .bb-github-link:hover {
        background: rgba(255,255,255,0.3);
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
    st.markdown(f"""
    <div class="bb-header">
        <a href="{https://github.com/Pw7992/Challenge_Alura_Agent_bimbambuy_support.git}" target="_blank" class="bb-github-link">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
                0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01
                1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95
                0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18
                1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82
                1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
                0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            GitHub
        </a>
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