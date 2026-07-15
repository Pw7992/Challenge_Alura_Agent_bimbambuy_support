import streamlit as st
st.title("Hello, Streamlit!")
st.write("Si ves esto, Streamlit funciona correctamente 🎉")

"""
app.py
Interfaz Streamlit para el agente de soporte BimBam Buy.
Conecta la cadena RAG (Cohere + Chroma) con logging en Oracle APEX (ORDS).
"""

import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

from src.rag_chain import BimBamBuyAgent

load_dotenv()

OCI_LOG_ENDPOINT = os.getenv("OCI_LOG_ENDPOINT")

st.set_page_config(
    page_title="BimBam Buy Support",
    page_icon="🛍️",
    layout="centered",
)


def log_to_oracle(pregunta, respuesta, fuentes, tiempo_ms):
    """Registra la ejecución en Oracle Autonomous DB vía ORDS (servicio OCI)."""
    if not OCI_LOG_ENDPOINT:
        return
    try:
        requests.post(
            OCI_LOG_ENDPOINT,
            json={
                "pregunta": pregunta,
                "respuesta": respuesta,
                "fuentes": ", ".join(fuentes) if fuentes else "",
                "tiempo_ms": tiempo_ms,
            },
            timeout=5,
        )
    except requests.RequestException as e:
        print(f"[warn] No se pudo registrar en Oracle: {e}")


@st.cache_resource(show_spinner=False)
def load_agent():
    """Carga el agente una sola vez por sesión de servidor (costoso de inicializar)."""
    return BimBamBuyAgent()


def main():
    st.title("🛍️ BimBam Buy — Soporte al Cliente")
    st.caption(
        "Pregúntame sobre reembolsos, envíos, garantías, métodos de pago "
        "o el programa de afiliados de BimBam Buy."
    )

    with st.spinner("Cargando agente..."):
        try:
            agent = load_agent()
        except Exception as e:
            st.error(f"No se pudo inicializar el agente: {e}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input del usuario
    question = st.chat_input("Escribe tu pregunta...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Buscando en la documentación..."):
                result = agent.ask(question)

            answer = result["answer"]
            sources = result["sources"]

            st.markdown(answer)
            if sources:
                st.caption(f"📄 Fuentes: {', '.join(sources)}")

            log_to_oracle(
                pregunta=question,
                respuesta=answer,
                fuentes=sources,
                tiempo_ms=result["elapsed_ms"],
            )

        st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.sidebar:
        st.subheader("ℹ️ Acerca del agente")
        st.markdown(
            """
            **BimBam Buy Support** es un agente RAG que responde
            preguntas basándose únicamente en la documentación oficial:

            - Política de Reembolsos y Devoluciones
            - Guía de Tiempos y Costos de Envío
            - Manual de Garantía de Productos
            - Preguntas Frecuentes sobre Métodos de Pago
            - Programa de Afiliados
            """
        )
        if st.button("🗑️ Limpiar conversación"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()