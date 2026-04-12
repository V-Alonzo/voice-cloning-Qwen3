import gradio as gr

def generateAudioPlayer(audioPath):
    audioPlayer = gr.Audio(value=audioPath, label="Cloned Voice Output")
    return audioPlayer
