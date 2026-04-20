import soundfile as sf
import gradio as gr
import inputsGenerator
import voiceClonning
import os
from informationExtraction import chatGeneration, initialConfiguration
from dotenv import load_dotenv
from gradio import ChatMessage

global baseAudio
global baseAudioTranscription

pdfFile = None
messagesHistory = []
baseAudio = None
baseAudioTranscription = None
outputAudioPath = None
personName = ""
personSummary = ""
textHistory = []
defaultTextToSynthesize = "Esto es lo que sucede cuando clonas una voz utilizando Inteligencia Artificial. Es sorprendente, ¿No te parece?"
generateWithVoiceCloning = True
reasoningActivated = False

load_dotenv(dotenv_path=".env", override=True)

def toggleVoiceCloning(value):
    global generateWithVoiceCloning
    generateWithVoiceCloning = value
    return value

def toggleReasoning(value):
    global reasoningActivated
    reasoningActivated = value
    return value


def processChatMessages(mensaje, historial):
    global textHistory
    global reasoningActivated

    responses = chatGeneration(mensaje, textHistory, reasoningActivated)

    chatMessages = []

    if(reasoningActivated):
        chatMessages.append(ChatMessage(role="assistant", content="Iniciando Razonamiento..."))

        for responseIndex in range(len(responses) - 1):
            chatMessages.append(ChatMessage(role="assistant", content=responses[responseIndex]))

        chatMessages.append(ChatMessage(role="assistant", content="Razonamiento Finalizado."))

    audio_response = None
    
    try:
        if generateWithVoiceCloning:
            audio_response = voiceClonning.performVoiceInference(responses[-1])
    except Exception as e:
        print(f"Error during voice inference: {e}")
        audio_response = None

    if(audio_response is None):
        chatMessages.append(ChatMessage(role="assistant", content=responses[-1]))
        return chatMessages
    
    chatMessages.append(ChatMessage(role="assistant", content=responses[-1]))
    chatMessages.append(ChatMessage(role="assistant", content=gr.Audio(value=audio_response)))
    
    return chatMessages

def processName(name):
    global personName
    personName = name
    print(f"Person name: {personName}")
    return name

def processPersonSummary(summary):
    global personSummary
    personSummary = summary
    print(f"Person summary: {personSummary}")
    return summary

def processPDF(file):
    global pdfFile

    if file is None:
        return "No file uploaded."
    
    pdfFile = file.name
    print(f"PDF file uploaded: {pdfFile}")
    return file

def processBaseAudio(filePath):
    global baseAudio
    baseAudio = filePath
    print(f"Base audio: {baseAudio}")
    return filePath

def processBaseAudioTranscription(transcription):
    global baseAudioTranscription
    baseAudioTranscription = transcription
    print(f"Base audio transcription: {baseAudioTranscription}")
    return transcription

def performVoiceCloning():
    global baseAudio
    global baseAudioTranscription

    if baseAudio is None or baseAudioTranscription is None:
        return "Base audio or transcription not provided."
    
    voiceClonning.performVoiceCloning(baseAudio, baseAudioTranscription)

    return "Voice cloning model loaded and clone prompt created."

def generateStep1():
    with gr.Blocks() as step1:
        gr.Markdown("## Step 1: Upload Base Audio File")
        fileInput = inputsGenerator.generateAudioInput(onUploadFunction = lambda x: processBaseAudio(x))

    return step1

def generateStep2():
    with gr.Blocks() as step2:
        gr.Markdown("## Step 2: Base Audio Transcription")
        multiLineTextInput = inputsGenerator.generateMultilineTextInput(onUploadFunction = lambda x: processBaseAudioTranscription(x), label = "Base Audio Transcription")

    return step2

def generateStep3():
    with gr.Blocks() as step3:
        gr.Markdown("## Step 3: Generating Cloned Voice")
        statusOutput = gr.Textbox(label = "Status", interactive = False)
        loadModelButton = gr.Button("Load Model")
        loadModelButton.click(fn = performVoiceCloning, inputs = [], outputs = [statusOutput])

        multilineTextInput = gr.Textbox(
            lines = 5,
            value = defaultTextToSynthesize,
            label = "Text to Synthesize",
            placeholder = "Type the text that will be generated with the cloned voice"
        )

        generateButton = gr.Button("Synthesize Cloned Voice")
        outputAudio = gr.Audio(label = "Cloned Voice Output")
        generateButton.click(
            fn = voiceClonning.performVoiceInference,
            inputs = [multilineTextInput],
            outputs = [outputAudio]
        )

    return step3

def generateStep4():
    with gr.Blocks() as step4:
        gr.Markdown("## Step 4: Upload PDF File and Basic Information")
        pdfInput = inputsGenerator.generatePDFInput(onUploadFunction = lambda x: processPDF(x))
        personNameInput = inputsGenerator.generateMultilineTextInput(onUploadFunction = lambda x: processName(x), label = "Person Name")
        personSummaryInput = inputsGenerator.generateMultilineTextInput(onUploadFunction = lambda x: processPersonSummary(x), label = "Person Summary")

    return step4

def generateStep5():
    global pdfFile
    global personName
    global personSummary
    global generateWithVoiceCloning

    with gr.Blocks() as step5:
        gr.Markdown("## Step 5: Chat with the Cloned Voice Agent")
        statusOutputChat = gr.Textbox(label = "Status", interactive = False)
        loadChatButton = gr.Button("Load Chat")
        loadChatButton.click(fn = lambda x: initialConfiguration(pdfFile, personSummary, personName), inputs = [], outputs = [statusOutputChat])
        toggleVoiceCloningCheckbox = inputsGenerator.generateCheckbox(label = "Generate with Voice Cloning", defaultValue = generateWithVoiceCloning, onChangeFunction = lambda x: toggleVoiceCloning(x))
        toggleReasoningCheckbox = inputsGenerator.generateCheckbox(label = "Activate Reasoning", defaultValue = reasoningActivated, onChangeFunction = lambda x: toggleReasoning(x))

        gr.ChatInterface(processChatMessages)

    return step5


steps = [generateStep1, generateStep2, generateStep3, generateStep4, generateStep5]


renderedStep = 0
with gr.Blocks() as demo:
    gr.Markdown("# Voice Cloning Activity")
    gr.Markdown("## Author: Víctor Alonzo Estévez Chávez")
    
    while renderedStep < len(steps):
        step = steps[renderedStep]

        with gr.Tab(f"Step {renderedStep + 1}"):
            step()

        renderedStep += 1


demo.launch()