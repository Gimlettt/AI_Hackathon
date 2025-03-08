from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import json
import simpleaudio as sa
from pydub import AudioSegment
from io import BytesIO

#from audio.record import record_voice
from record import record_voice

# Load .env file from the root of the project
load_dotenv()

# Get the API key
OpenAI.api_key = os.getenv('API_KEY')

RECORDED_FILE_NAME = "audio/recorded_for_GPT.wav"
#RECORDED_FILE_NAME = 'audio/input_audio.wav'
record_voice(RECORD_SECONDS=8, OUTPUT_FILENAME = RECORDED_FILE_NAME)

# Read the audio file
with open(RECORDED_FILE_NAME, 'rb') as audio_file:
    audio_input = audio_file.read()
    # Encode the binary data to base64
    encoded_audio = base64.b64encode(audio_input).decode('utf-8')


client = OpenAI(api_key = os.getenv('API_KEY'))

completion = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "wav"},
    
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Give separate contents in the returned audio and text. In the audio only, encourage the user to be positive without reading out the score. In the returned text only, rate the user's mood from 1 to 10, where 10 is the highest mood."
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": encoded_audio,
                        "format": "wav"
                    }
                }
            ]
        },
    ]
)

print(completion.choices[0].message)

encoded_audio = completion.choices[0].message.audio.data
#encoded_audio = completion.choices[0].message.content.get('audio_output','')
#returned_text = completion.choices[0].message.content.get('text_output', '')
#print(returned_text)

# Decode the base64 string back to binary audio data
audio_data = base64.b64decode(encoded_audio)

# Convert the binary data to an audio file-like object
audio_file = BytesIO(audio_data)

# Load the audio into a format that can be played
audio = AudioSegment.from_wav(audio_file)

# Export the audio to a temporary WAV file
audio.export("audio/output.wav", format="wav")

# Play the audio
wave_obj = sa.WaveObject.from_wave_file("audio/output.wav")
play_obj = wave_obj.play()
play_obj.wait_done()  # Wait until the audio finishes playing
