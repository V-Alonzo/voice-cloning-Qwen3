from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import json
import os

import gradio as gr
from pydantic import BaseModel

load_dotenv(dotenv_path=".env", override=True)

openAiClient = OpenAI()
summary = None
profile = None
name = None
systemPrompt = None
evaluatorSystemPrompt = None
geminiModel = "gemini-2.5-flash"
geminiBaseURL = "https://generativelanguage.googleapis.com/v1beta/openai/"


gemini = OpenAI(
        api_key= os.getenv("GEMINI_API_KEY"),
        base_url = geminiBaseURL
)

registerUserTool = {
    "name": "registerDataUser",
    "description": "Usa esta herramienta para registrar cuando un usuario está interesado en contactar y proporciona su email",
    "parameters": {
        "type": "object",
        "properties": {
            "correo": {
                "type": "string",
                "description": "La dirección de email del usuario"
            },
            "nombre": {
                "type": "string",
                "description": "El nombre del usuario, si lo proporcionó"
            },
            "notas": {
                "type": "string",
                "description": "Cualquier información adicional sobre la conversación que valga la pena registrar"
            }
        },
        "required": ["correo"],
        "additionalProperties": False
    }
}

registerUnknownQuestionTool = {
        "name": "registerUnknownQuestion",
        "description": "Siempre usa esta herramienta para registrar cualquier pregunta cuya respuesta no se pueda encontrar en el contexto proporcionado.",
        "parameters": {
            "type": "object",
            "properties": {
                "pregunta": {
                    "type": "string",
                    "description": "La pregunta que no pudo ser respondida"
                }
            },
            "required": ["pregunta"],
            "additionalProperties": False
        }
    }

tools = [
        {"type": "function", "function": registerUserTool},
        {"type": "function", "function": registerUnknownQuestionTool}
    ]


def initialConfiguration(pdfFilePath, personSummary, personName):
    global openAiClient
    global profile
    global systemPrompt
    global evaluatorSystemPrompt
    global gemini
    global registerUserTool
    global registerUnknownQuestionTool
    global tools
    global summary
    global name

    name = personName
    summary = personSummary

    print(f"PDF file path: {pdfFilePath}")

    pdfReader = PdfReader(pdfFilePath)
    profile = ""

    for page in pdfReader.pages:
        pageText = page.extract_text()
        if pageText:
            profile += pageText

    systemPrompt = f"""
        Estás actuando como {name}. 
        Estás respondiendo preguntas en el sitio web de {name}, particularmente preguntas relacionadas con la carrera, antecedentes, habilidades y experiencia de {name}. 
        Tu responsabilidad es representar a {name} para las interacciones en el sitio web de la manera más fiel posible. Se te proporciona un resumen de los antecedentes de {name} y el perfil que puedes usar para responder preguntas. 
        Sé profesional y atractivo como si hablaras con un cliente potencial o futuro empleador que se encontró con el sitio web. 
        Si no sabes algo, dilo.

        ## Resumen: 
        {summary}

        ## Perfil:
        {profile}

        Con este contexto, por favor chatea con el usuario, manteniéndote siempre en el personaje {name}."""
    
    evaluatorSystemPrompt = f"""

        Eres un evaluador que decide si una respuesta a una pregunta es aceptable. Se te proporciona una conversación entre un usuario y un agente. Tu tarea es decidir si la última respuesta del agente es de calidad aceptable. El agente está interpretando el papel de {name} y está representando a {name} en su sitio web. Se le ha instruido al agente que sea profesional y atractivo, como si hablara con un cliente potencial o futuro empleador que se encontró con el sitio web. Se le ha proporcionado al agente contexto sobre {name} en forma de resumen y detalles de su perfil. Aquí está la información:

        ##Resumen:
        {summary}

        ##Perfil:
        {profile}

        Con este contexto, por favor evalúa la última respuesta, respondiendo a la pregunta: '¿La respuesta del agente es de calidad aceptable?'

        \n\nResponde ÚNICAMENTE con un objeto JSON con los campos 'isAcceptable' (boolean) y 'feedback' (string) sin texto adicional

    """

    return "Chat Initiated"

def chatGeneration(message, history, reasoningActivated):
    return chatear(message, history, reasoningActivated)

def getOpenAIResponse(messages):
    global geminiModel
    response = openAiClient.chat.completions.create(model = "gpt-4o-mini", 
                                                    messages = messages,
                                                    tools = tools)
    
    endingReason = response.choices[0].finish_reason

    newResponses = []

    if endingReason == "tool_calls":
        print("La IA ha solicitado llamar a una herramienta. Ejecutando herramientas...")
        IAMessage = response.choices[0].message
        toolCalls = IAMessage.tool_calls
        results = manageToolCalls(toolCalls)
        
        for result in results:
            newResponses.append(result["content"]["message"])

    else:
        newResponses.append(response.choices[0].message.content)
    
    return newResponses


def chatear (message, history, reasoningActivated):
    messages = [{"role":"system","content": systemPrompt}] + history + [{"role":"user","content": message}]
    responses = []
    newResponses = getOpenAIResponse(messages)                                  

    if reasoningActivated:
        evaluation = evaluate(newResponses, message, history)

        responses.append(f"----------Evaluando respuestas---------\n {newResponses}\n")
        responses.append(f"----------Retroalimentación---------\n- {evaluation.feedback}\n")

        while not evaluation.isAcceptable:
            responses.append(f"Generando nueva respuesta...")
            newSystemPrompt = rerun(newResponses, feedback = evaluation.feedback)
            messages = [{"role":"system","content": newSystemPrompt}] + history + [{"role":"user","content": message}]
            
            newResponses = getOpenAIResponse(messages)

            evaluation = evaluate(newResponses, message, history)

            responses.append(f"----------Evaluando respuestas---------\n {newResponses}\n")
            responses.append(f"----------Retroalimentación----------\n {evaluation.feedback}\n")


        responses.append(f"----------Respuesta final---------\n {newResponses[-1]}\n")

        return responses
    
    responses += newResponses

    return responses

class Evaluacion(BaseModel):
    isAcceptable: bool
    feedback: str


def rerun(response, feedback):
    global systemPrompt

    updatedSystemPrompt = systemPrompt + f"\n\n ## Respuesta anterior rechazada\nAcabas de intentar responder, pero el control de calidad rechazó tu respuesta\n"
    updatedSystemPrompt += f"## Tu respuesta intentada: \n{response}\n\n"
    updatedSystemPrompt += f"## Razón del rechazo: \n{feedback}\n\n"

    return updatedSystemPrompt


def promptEvaluatorUser(responses, message, history):
    userPrompt = f"Aqui está la conversacion entre el usuario y el agente: \n\n{history}\n\n"
    userPrompt += f"Aqui esta el ultimo mensaje del usuario: \n\n{message}\n\n"
    userPrompt += f"Aqui esta la ultima respuesta del agente: \n\n{responses}\n\n"
    userPrompt += "Por favor evalua la respuesta, respondiendo si es aceptable y tu retroalimentacion"
    return userPrompt


def evaluate (responses, message, history) -> Evaluacion:
    messages = [
        {"role":"system","content": evaluatorSystemPrompt},
        {"role":"user","content": promptEvaluatorUser(responses, message, history)}
    ]
    
    evaluationResponse = gemini.chat.completions.create(
        model= geminiModel,
        messages=messages,
        response_format={"type": "json_object"}
    )

    content = evaluationResponse.choices[0].message.content
    print("RAW GEMINI: ", content)
    
    data = json.loads(content)
    return Evaluacion(**data)

def registerDataUser(correo,nombre="No proporcionado", notas="No proporcionado"):
    """Registra los datos de un usuario interesado"""
    print(f" Nuevo Contacto: {nombre} con email {correo} y notas: {notas}")
    with open ("ToolsResults/contactos.txt","a", encoding="utf-8") as f:
        f.write(f"Nombre: {nombre} | Email: {correo} | Notas: {notas} \n")
    return {"status": "OK", "message": f"¡Gracias {nombre}, hemos registrado tu interés y nos pondremos en contacto contigo pronto!"}


def registerUnknownQuestion(pregunta):
    """Registra pregunta que el chatbot no pudo responder"""
    print(f"PREGUNTA SIN RESPUESTA:{pregunta}")
    with open("ToolsResults/preguntas_sin_respuesta.txt","a", encoding="utf-8") as f:
        f.write(f"Pregunta: {pregunta}\n")
    return {"status": "OK", "message": "No puedo responder a tu pregunta, pero la hemos registrado, sigo aprendiendo."}


def manageToolCalls(llamadas_herramientas):
    # Ejecuta las herramientas que solicita la IA
    resultados = []

    for llamada in llamadas_herramientas:
        nombre_herramienta = llamada.function.name
        argumentos = json.loads(llamada.function.arguments)

        print(f"> Herramienta ejecutada: {nombre_herramienta}", flush=True)

        if nombre_herramienta == "registerDataUser":
            resultado = registerDataUser(**argumentos)

        elif nombre_herramienta == "registerUnknownQuestion":
            resultado = registerUnknownQuestion(**argumentos)
        else:
            resultado = {"error": "Herramienta no encontrada"}

        resultados.append({
            "role": "assistant",
            "content": resultado,
            "tool_call_id": llamada.id
        })
    return resultados