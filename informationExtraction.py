from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import json
import os

import gradio as gr
from pydantic import BaseModel

global openAiClient
global summary
global profile
global name
global systemPrompt
global evaluatorSystemPrompt
global gemini

load_dotenv(dotenv_path=".env", override=True)
systemPrompt = ""

def initialConfiguration(pdfFilePath, personSummary, personName):
    global openAiClient
    global summary
    global profile
    global name
    global systemPrompt
    global evaluatorSystemPrompt
    global gemini

    name = personName
    openAiClient = OpenAI()
    summary = personSummary
    gemini = OpenAI(
        api_key= os.getenv("GEMINI_API_KEY"),
        base_url = os.getenv("GEMINI_BASE_URL")
    )

    print(f"PDF file path: {pdfFilePath}")

    pdfReader = PdfReader(pdfFilePath)
    profile = ""

    for page in pdfReader.pages:
        pageText = page.extract_text()
        if pageText:
            profile += pageText

    systemPrompt = os.getenv("SYSTEM_PROMPT").replace("{nombre}", name).replace("{resumen}", summary).replace("{perfil}", profile)

    evaluatorSystemPrompt = f"Eres un evaluador que decide si una respuesta a una pregunta es aceptable. Se te proporciona una conversación entre un usuario y un agente. Tu tarea es decidir si la última respuesta del agente es de calidad aceptable. El agente está interpretando el papel de {name} y está representando a {name} en su sitio web. Se le ha instruido al agente que sea profesional y atractivo, como si hablara con un cliente potencial o futuro empleador que se encontró con el sitio web. Se le ha proporcionado al agente contexto sobre {name} en forma de resumen y detalles de su perfil. Aquí está la información:"

    evaluatorSystemPrompt += f"\n\n ##Resumen: \n{summary}\n\nPerfi\n{profile}\n\n "

    evaluatorSystemPrompt += f"Con este contexto,, por favor evalúa la última respuesta, respoindiendo a la pregunta: '¿La respuesta del agente es de calidad aceptable?'"

    evaluatorSystemPrompt += f"\n\nResponde ÚNICAMENTE con un objeto JSON con los campos 'isAcceptable' (boolean) y 'feedback' (string) sin texto adicional"

    return "Chat Initiated"

def chatGeneration(message, history, reasoningActivated):
    return chatear(message, history, reasoningActivated)

def chatear (message, history, reasoningActivated):
    messages = [{"role":"system","content": systemPrompt}] + history + [{"role":"user","content": message}]
    responses = []
    response = openAiClient.chat.completions.create(model= os.getenv("GPT_MODEL"), messages = messages)

    if reasoningActivated:
        evaluation = evaluar(response, message, history)

        responses.append(f"----------Evaluando respuesta---------\n {response.choices[0].message.content}\n")
        responses.append(f"----------Retroalimentación---------\n- {evaluation.feedback}\n")

        while not evaluation.isAcceptable:
            responses.append(f"Generando nueva respuesta...")
            newSystemPrompt = rerun(response, feedback = evaluation.feedback)
            messages = [{"role":"system","content": newSystemPrompt}] + history + [{"role":"user","content": message}]
            
            response = openAiClient.chat.completions.create(model= os.getenv("GPT_MODEL"), messages = messages)

            evaluation = evaluar(response, message, history)

            responses.append(f"----------Evaluando respuesta---------\n {response.choices[0].message.content}\n")
            responses.append(f"----------Retroalimentación----------\n {evaluation.feedback}\n")


        responses.append(f"----------Respuesta final---------\n {response.choices[0].message.content}\n")

        return responses
    
    responses.append(response.choices[0].message.content)

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


def prompt_usuario_evaluador(response, message, history):
    userPrompt = f"Aqui está la conversacion entre el usuario y el agente: \n\n{history}\n\n"
    userPrompt += f"Aqui esta el ultimo mensaje del usuario: \n\n{message}\n\n"
    userPrompt += f"Aqui esta la ultima respuesta del agente: \n\n{response}\n\n"
    userPrompt += "Por favor evalua la respuesta, respondiendo si es aceptable y tu retroalimentacion"
    return userPrompt


def evaluar (response, message, history) -> Evaluacion:
    messages = [
        {"role":"system","content": evaluatorSystemPrompt},
        {"role":"user","content": prompt_usuario_evaluador(response, message, history)}
    ]
    
    evaluationResponse = gemini.chat.completions.create(
        model= os.getenv("GEMINI_MODEL"),
        messages=messages,
        response_format={"type": "json_object"}
    )

    content = evaluationResponse.choices[0].message.content
    print("RAW GEMINI: ", content)
    
    data = json.loads(content)
    return Evaluacion(**data)
