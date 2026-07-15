"""
src/ingest.py
Lee los PDFs de knowledge_base/, los divide en chunks y genera
el índice vectorial en vector_db/ usando embeddings de Cohere.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

COHERE_API_KEY = os.getenv("COHERE_API_KEY")


def load_documents():
    """Carga todos los PDFs de knowledge_base/ con metadatos por archivo."""
    all_docs = []
    pdf_files = list(KNOWLEDGE_BASE_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No se encontraron PDFs en {KNOWLEDGE_BASE_DIR}"
        )

    for pdf_path in pdf_files:
        print(f"Cargando: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()

        # Metadato de categoría a partir del nombre del archivo
        for doc in docs:
            doc.metadata["source_file"] = pdf_path.name
            doc.metadata["category"] = "E-commerce / BimBam Buy"

        all_docs.extend(docs)

    print(f"Total de páginas cargadas: {len(all_docs)}")
    return all_docs


def split_documents(documents):
    """Divide los documentos en chunks con overlap para no cortar ideas."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Total de chunks generados: {len(chunks)}")
    return chunks


def build_vector_store(chunks):
    """Genera embeddings con Cohere y los guarda en Chroma (local, persistente)."""
    embeddings = CohereEmbeddings(
        cohere_api_key=COHERE_API_KEY,
        model="embed-multilingual-v3.0",  # bueno para español
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
        collection_name="bimbam_buy_support",
    )
    print(f"Índice vectorial guardado en: {VECTOR_DB_DIR}")
    return vector_store


def main():
    if not COHERE_API_KEY:
        raise ValueError(
            "Falta COHERE_API_KEY en tu archivo .env. "
            "Consigue una gratis en https://dashboard.cohere.com/api-keys"
        )

    documents = load_documents()
    chunks = split_documents(documents)
    build_vector_store(chunks)
    print("✅ Ingesta completa.")


if __name__ == "__main__":
    main()