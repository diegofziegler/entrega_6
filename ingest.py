import os
import glob
import warnings
from dotenv import load_dotenv

# Ignorar advertencias innecesarias de deprecación de paquetes secundarios
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from logger import get_rag_logger

load_dotenv()

logger = get_rag_logger()

VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "./vectorstore")
DATA_DIR = os.getenv("DATA_DIR", "./data")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")


def get_embeddings_model():
    logger.info(f"Cargando modelo de embeddings HuggingFace: {EMBEDDING_MODEL_NAME}")
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def run_ingestion():
    logger.info(f"Iniciando proceso de ingesta desde directorio: {DATA_DIR}")
    if not os.path.exists(DATA_DIR):
        logger.error(f"El directorio de datos {DATA_DIR} no existe.")
        raise FileNotFoundError(f"El directorio de datos {DATA_DIR} no existe.")

    files = glob.glob(os.path.join(DATA_DIR, "*.md")) + glob.glob(os.path.join(DATA_DIR, "*.txt"))
    if not files:
        logger.warning(f"No se encontraron archivos .md o .txt en {DATA_DIR}")
        return

    logger.info(f"Se encontraron {len(files)} archivos para procesar: {[os.path.basename(f) for f in files]}")

    documents = []
    for file_path in files:
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = os.path.basename(file_path)
            documents.extend(docs)
        except Exception as e:
            logger.error(f"Error cargando archivo {file_path}: {e}")

    logger.info(f"Cargados {len(documents)} documentos. Aplicando chunking...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Generados {len(chunks)} fragmentos (chunks).")

    embeddings = get_embeddings_model()

    logger.info(f"Guardando fragmentos en ChromaDB persistente en: {VECTORSTORE_DIR}")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR
    )
    logger.info("Ingesta completada exitosamente.")
    return vectorstore


def check_and_ensure_vectorstore():
    if not os.path.exists(VECTORSTORE_DIR) or not os.listdir(VECTORSTORE_DIR):
        logger.info(f"Vector DB no encontrada o vacía en {VECTORSTORE_DIR}. Ejecutando ingesta automática...")
        run_ingestion()
    else:
        logger.info(f"Vector DB detectada existente en {VECTORSTORE_DIR}.")


if __name__ == "__main__":
    run_ingestion()
