import torch
import soundfile as sf
import os
from qwen_tts import Qwen3TTSModel

#Verify if CUDA (GPU) is available, otherwise use CPU.

clonnedVoice = None
model = None

def getBestDeviceAndDtype():
    if torch.backends.mps.is_available():
        return "mps", torch.float16

    if torch.cuda.is_available():
        return "cuda", torch.bfloat16

    return "cpu", torch.float32

def loadModel():
    global model

    device, dtype = getBestDeviceAndDtype()
    print(f"Using device: {device}")

    if device == "cuda":
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    elif device == "mps":
        print("Using Apple Silicon GPU via MPS.")
    else:
        print("No GPU found, using CPU.")

    model_name = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"

    print("Loading model...")

    customVoiceModel = Qwen3TTSModel.from_pretrained(
        model_name,
        device_map = "auto",
        dtype = dtype
    )

    print("Model loaded successfully.")

    model = customVoiceModel


def performVoiceCloning(baseAudio, baseAudioTranscription):
    global clonnedVoice
    
    loadModel()

    clonnedVoice = model.create_voice_clone_prompt(
        ref_audio = baseAudio,
        ref_text = baseAudioTranscription
    )


def performVoiceInference(textToSynthesize, language = "Spanish"):
    global clonnedVoice
    global model 

    if clonnedVoice is None:
        print("No cloned voice available. Please perform voice cloning first.")
        return None
    
    wavs, sr = model.generate_voice_clone(
        text = textToSynthesize,
        language = language,
        voice_clone_prompt = clonnedVoice
    )

    sf.write("synthesized_audio.wav", wavs[0], sr)

    return "synthesized_audio.wav"