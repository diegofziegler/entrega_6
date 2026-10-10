import os
import warnings
from typing import List, Dict, Any
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=DeprecationWarning)

from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from logger import get_rag_logger
from ingest import check_and_ensure_vectorstore, get_embeddings_model

load_dotenv()

logger = get_rag_logger()

VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "./vectorstore")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-3-flash-preview")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class RAGResponse(BaseModel):
    answer: str = Field(description="Respuesta generada basada estrictamente en el contexto recuperado")
    sources: List[str] = Field(description="Lista de fuentes (archivos) utilizadas para construir la respuesta")
    found_context: bool = Field(description="Verdadero si se encontró información relevante en los documentos, falso de lo contrario")


def get_vectorstore():
    check_and_ensure_vectorstore()
    embeddings = get_embeddings_model()
    return Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )


async def get_rag_response(query: str, k: int = 4) -> RAGResponse:
    logger.info(f"RAG Request - Query: '{query}'")

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    logger.info(f"Buscando fragmentos relevantes (k={k})...")
    docs = await retriever.ainvoke(query)

    sources = list(set(doc.metadata.get("source", "desconocido") for doc in docs))
    context_text = "\n\n---\n\n".join([f"Fuente [{doc.metadata.get('source')}]: {doc.page_content}" for doc in docs])

    logger.info(f"Fragmentos recuperados: {len(docs)} de fuentes {sources}")

    parser = PydanticOutputParser(pydantic_object=RAGResponse)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Eres un asistente técnico especializado en la base de conocimientos provista.\n"
         "Responde a la consulta basándote ÚNICAMENTE en el CONTEXTO proporcionado.\n"
         "Si el contexto no contiene suficiente información para responder la pregunta, establece `found_context` en False y responde claramente que no dispones de esa información en los documentos.\n"
         "Si encuentras la respuesta, establece `found_context` en True y detalla la respuesta basándote en el contexto.\n\n"
         "{format_instructions}"),
        ("human", "CONTEXTO:\n{context}\n\nPREGUNTA: {query}")
    ])

    prompt_formatted = prompt.format(
        context=context_text,
        query=query,
        format_instructions=parser.get_format_instructions()
    )

    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.0
    )

    logger.info(f"Invocando LLM ({LLM_MODEL_NAME}) de forma asíncrona...")
    response_msg = await llm.ainvoke(prompt_formatted)

    try:
        parsed_response = parser.parse(response_msg.content)
        parsed_response.sources = sources if parsed_response.found_context else []
        logger.info(f"Respuesta RAG generada. found_context={parsed_response.found_context}")
        return parsed_response
    except Exception as e:
        logger.error(f"Error parseando respuesta RAG: {e}")
        return RAGResponse(
            answer=response_msg.content,
            sources=sources,
            found_context=True
        )


def search_context_sync(query: str, k: int = 4) -> Dict[str, Any]:
    """
    Función síncrona auxiliar usada como herramienta por los agentes.
    """
    logger.info(f"Búsqueda vectorial síncrona - Query: '{query}'")
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=k)
    sources = list(set(doc.metadata.get("source", "desconocido") for doc in docs))
    context_text = "\n\n---\n\n".join([f"Fuente [{doc.metadata.get('source')}]: {doc.page_content}" for doc in docs])

    logger.info(f"Búsqueda síncrona recuperó {len(docs)} fragmentos de {sources}")
    return {
        "context": context_text,
        "sources": sources,
        "num_chunks": len(docs)
    }
