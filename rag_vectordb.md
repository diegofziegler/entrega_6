# Pre-entrega 3: Sistema de recuperación semántica local (RAG)

## ¿Qué debes construir?

Debes entregar un script Python que implemente un flujo **End-to-End de RAG**. El sistema debe ser capaz de recibir una consulta del usuario, buscar la información relevante en una base vectorial previamente poblada y generar una respuesta queutilice *exclusivamente* esa información.

## Componentes a entregar:

1. **Módulo de Ingesta (Setup):** Una función que tome un conjunto de documentos (pueden ser archivos `.txt` o `.md` simples), los fragmente (*chunking*) y los persista en una colección de **ChromaDB**.
2. **Capa de Recuperación (Retriever):** Una lógica que convierta la pregunta del usuario en un embedding y recupere los fragmentos más relevantes.
3. **Generación Grounded:** Una cadena de **LangChain (LCEL)** que reciba los documentos recuperados y la pregunta, generando una respuesta. El prompt debe instruir al modelo a decir "No lo sé" si la respuesta no está en el contexto.


## Pasos sugeridos

1. **Puebla tu "Cerebro":** Elige 3 o 4 archivos de texto sobre un tema específico (ej. manuales técnicos, apuntes de clase o normativas). Usa las técnicas de *RecursiveCharacterTextSplitter* que vimos en la Unidad 2 para procesarlos. Los archivos de texto están en el directorio `./data`.
2. **Configura ChromaDB:** Inicializa el cliente persistente en una carpeta local (ej. `./vectorstore`). Asegúrate de usar el mismo modelo de embeddings para indexar y para consultar.
3. **Construye el Prompt de Sistema:** Diseña un prompt que actúe como un "filtro de veracidad". Ejemplo: *"Eres un asistente técnico. Responde solo basándote en el CONTEXTO proporcionado. Si la respuesta no está allí, di que no tienes acceso a esa información."*
4. **Crea la Cadena LCEL:** Une el retriever con el transformador de documentos y el modelo de lenguaje. Recuerda que el output debe pasar por un `PydanticOutputParser`.


## Errores comunes a evitar

- **El "Contexto Infinito":** No intentes pasar 50 fragmentos al LLM. Esto causará errores de límite de tokens o degradación de la atención del modelo (*Lost in the Middle*). Mantén un `top_k` de entre 3 y 5.
- **Embeddings no coincidentes:** Es el error #1. Si indexas tus documentos con `OpenAIEmbeddings` y consultas con `HuggingFaceEmbeddings`, la distancia vectorial no tendrá sentido y los resultados serán aleatorios.
- **Falta de persistencia:** Asegúrate de que el script verifique si la base de datos ya existe antes de volver a indexar todo, optimizando así el tiempo y costo de ejecución.

## Entregable esperado

- **Tipo:** Código — un repositorio de GitHub que contiene lo que detallamos a continuación.
- **Script de ingesta:** el repo contiene el script de ingesta (chunking + ChromaDB).
- **Script de RAG ASINCRONO:** el script de la cadena RAG asíncrona que procesa los archivos considerados como dataset.
- **Archivos Dataset:** un dataset de ejemplo compuesto por archivos (`.txt`/`.md`)
- **Documentación que explica el uso:** un archivo `README.md` con los detalles que explican como preparar el ambiente, como ejecutar el ejemplo.
- **Qué NO hace falta:** no es un documento de análisis; el `README.md` alcanza como documentación.

### Detalles del entregable

1. Crea un entorno virtual con la herramienta `uv` e instala las dependencias necesarias: `langchain`, `chromadb`, `openai` (o el provider seleccionado), y `pydantic`.
2. Implementa un script de carga que lea archivos de una carpeta `/data`, aplique un chunking estratégico (mínimo 500 tokens con 50 de overlap) y los guarde en una instancia local de ChromaDB.
3. Define una clase o función asíncrona `get_rag_response(query: str)` que: 
 - a. Realice una búsqueda de similitud en ChromaDB. 
 - b. Construya un prompt incluyendo los fragmentos recuperados. 
 - c. Llame al LLM de forma asíncrona. 
 - d. Parsee la respuesta a un modelo Pydantic que incluya el texto y las referencias.
4. Realiza dos pruebas: una pregunta cuya respuesta esté en los documentos y una "pregunta trampa" cuya respuesta no esté, verificando que el modelo no alucine.
5. Sube tu código asegurándote de no incluir llaves de API (usa variables de entorno `.env`).

