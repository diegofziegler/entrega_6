import os
import logging

LOG_DIR = os.getenv("LOG_DIR", "./log")
os.makedirs(LOG_DIR, exist_ok=True)

# Agent logger setup
agent_logger = logging.getLogger("agentes")
agent_logger.setLevel(logging.INFO)

agent_handler = logging.FileHandler(os.path.join(LOG_DIR, "agentes.log"), encoding="utf-8")
agent_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
agent_handler.setFormatter(agent_formatter)

if not agent_logger.handlers:
    agent_logger.addHandler(agent_handler)

# RAG logger setup
rag_logger = logging.getLogger("rag")
rag_logger.setLevel(logging.INFO)

rag_handler = logging.FileHandler(os.path.join(LOG_DIR, "rag.log"), encoding="utf-8")
rag_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
rag_handler.setFormatter(rag_formatter)

if not rag_logger.handlers:
    rag_logger.addHandler(rag_handler)


def get_agent_logger():
    return agent_logger


def get_rag_logger():
    return rag_logger
