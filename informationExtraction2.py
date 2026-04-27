import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import gradio as gr
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

documento = ""
chunks = []
rag_chain = None

#Sustiuir Agencia Digital por la empresa en cuestión
prompt = ChatPromptTemplate.from_template("""Eres el asistente virtual de Agencia Digital. Tu trabajo es respondeer las preguntas
de los clientes ÚNICAMENTE usando la información proporcionada en el contextto.

Reglas estrictas:
1. SOLO responde con información que está en el contexto.
2. Si la pregunta no se puede responder con el contexto, di:
"Lo siento, no tengo esa información. Te recomiendo contactarnos por whatsapp al +1234567890 por email a correo@gmail.com"
3. Sé amable, conciso y útil.
4. Si preguntan precios, siempre menciona que podemos hacer contacto con un agente.
5. Responde en español.

Contexto:
{context}

Pregunta del cliente: {question}

Respuesta:""")

def formatDocs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def getDefaultAgencyInformation():
    try:
        with open("agencia.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"No se pudo leer agencia.txt: {e}")
        return ""


def loadAgencyConfiguration(agencyInformation):
    global documento
    global chunks
    global rag_chain

    documento = (agencyInformation or "").strip()

    if not documento:
        rag_chain = None
        chunks = []
        return "La información de agencia está vacía."

    textSplitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
    )

    chunks = textSplitter.split_text(documento)

    vectorStore = FAISS.from_texts(chunks, embeddings)
    retriever = vectorStore.as_retriever(
        search_type="similarity",
        search_kwargs = {'k': 4}
    )

    rag_chain = (
        {"context": retriever | formatDocs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return f"Documento cargado: {len(chunks)} fragmentos indexados"


def chatGeneration2(message, history=None):
    global rag_chain

    if rag_chain is None:
        return "Primero carga la información de la agencia."

    return rag_chain.invoke(message)
