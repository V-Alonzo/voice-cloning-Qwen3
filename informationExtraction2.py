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

with open("agencia.txt","r", encoding="utf-8") as f:
    documento = f.read()
    
    
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

rag_chain = (
    {"context": retriever | formatDocs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def respond(message, history):
    response = rag_chain.invoke(message)
    return response

demo = gr.ChatInterface(
    fn = respond,
    title="Agencia Digital AI",
    description="Pregúntame sobre horarios, ubicación y más",
    examples = [
        "¿Cuál es el horario de atención?",
        "¿Tienen opciones Automaticaciones?",
        "¿Qué automatizaciones diseña?",
        "¿Usas Python para automatizar?",
        "Algún contacto para dudas"
    ]
)

if __name__ == "__main__":
    print (f"Documento cargado: {len(chunks)} fragmentos indexados")
    demo.launch(
        server_name ="0.0.0.0",
        server_port= 7861,
        theme ="soft",
        share= True
    )
