import soundfile as sf
import gradio as gr
import inputsGenerator
import voiceClonning

global baseAudio
global baseAudioTranscription

baseAudio = None
baseAudioTranscription = None
outputAudioPath = None
defaultTextToSynthesize = "Esto es lo que sucede cuando clonas una voz utilizando Inteligencia Artificial. Es sorprendente, ¿No te parece?"

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
        multiLineTextInput = inputsGenerator.generateMultilineTextInput(onUploadFunction = lambda x: processBaseAudioTranscription(x))

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


steps = [generateStep1, generateStep2, generateStep3]


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