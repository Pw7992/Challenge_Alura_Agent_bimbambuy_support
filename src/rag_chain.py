"""
src/rag_chain.py
Cadena RAG: recibe una pregunta, recupera contexto de Chroma
y genera una respuesta con Cohere, citando siempre la fuente.
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = BASE_DIR / "vector_db"
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Umbral de relevancia: si nada supera esto, el agente admite que no sabe
SIMILARITY_THRESHOLD = 0.35
TOP_K = 4

SYSTEM_PROMPT = """Eres el asistente de soporte de BimBam Buy, un e-commerce.
Respondes ÚNICAMENTE con base en el contexto proporcionado abajo, extraído
de la documentación oficial de la empresa (políticas de reembolso, envíos,
garantía, métodos de pago, atención al cliente y programa de afiliados).

Reglas estrictas:
1. Si la respuesta está en el contexto, respóndela de forma clara y directa.
2. SIEMPRE indica al final de tu respuesta de qué documento y página sacaste
   la información, con el formato: "Fuente: <nombre_del_archivo>, página <número>".
3. Si el contexto no contiene información suficiente para responder,
   di explícitamente: "No encontré esta información en la documentación
   disponible de BimBam Buy." y a continuación ofrece estos canales oficiales
   de contacto: chat en línea, correo electrónico soporte@bimbambuy.com,
   o teléfono (+506) 2233-4455. No inventes ningún otro dato de contacto
   distinto a estos tres.
4. No uses conocimiento externo a los documentos proporcionados.

Contexto:
{context}
"""


def _load_vector_store():
    embeddings = CohereEmbeddings(
        cohere_api_key=COHERE_API_KEY,
        model="embed-multilingual-v3.0",
    )
    return Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings,
        collection_name="bimbam_buy_support",
    )


def _format_docs(docs):
    """Junta los chunks recuperados en un solo bloque de texto con su fuente."""
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source_file", "desconocido")
        page = doc.metadata.get("page", "?")
        formatted.append(f"[Fuente: {source}, página {page}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


class BimBamBuyAgent:
    def __init__(self):
        self.vector_store = _load_vector_store()
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": TOP_K, "score_threshold": SIMILARITY_THRESHOLD},
        )
        self.llm = ChatCohere(
            cohere_api_key=COHERE_API_KEY,
            model="command-r-plus-08-2024",  # buen soporte multilingüe/RAG
            temperature=0.2,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "{question}"),
            ]
        )

    def ask(self, question: str) -> dict:
        """Ejecuta el pipeline completo y devuelve respuesta + metadatos."""
        start = time.time()

        docs = self.retriever.invoke(question)

        if not docs:
            answer = (
                "No encontré esta información en la documentación disponible "
                "de BimBam Buy. Te recomiendo contactar directamente a soporte "
                "al cliente."
            )
            sources = []
        else:
            context = _format_docs(docs)
            chain = self.prompt | self.llm | StrOutputParser()
            answer = chain.invoke({"context": context, "question": question})
            sources = list({doc.metadata.get("source_file", "desconocido") for doc in docs})

        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "elapsed_ms": elapsed_ms,
        }


if __name__ == "__main__":
    # Prueba rápida desde consola
    agent = BimBamBuyAgent()
    while True:
        q = input("\nPregunta (o 'salir'): ")
        if q.lower() == "salir":
            break
        result = agent.ask(q)
        print(f"\nRespuesta: {result['answer']}")
        print(f"Fuentes: {', '.join(result['sources']) if result['sources'] else 'ninguna'}")
        print(f"Tiempo: {result['elapsed_ms']} ms")