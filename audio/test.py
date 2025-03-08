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
record_voice(RECORD_SECONDS=7, OUTPUT_FILENAME = RECORDED_FILE_NAME)

# Read the audio file
with open(RECORDED_FILE_NAME, 'rb') as audio_file:
    audio_input = audio_file.read()
    # Encode the binary data to base64
    encoded_audio = base64.b64encode(audio_input).decode('utf-8')


client = OpenAI(api_key = os.getenv('API_KEY'))

list_of_event_names = ["3A1 coursework", "3F2 FTR", "3C5 lab report", "General", "Hackathon"]

PROMPT = f"""
You are an assistant analyzing a user's mood and what event they are referring to based on their audio input.
Important: Return the results ONLY in a JSON format like this:\n\n{{\"event_name\": \"[Selected Task Name]\", \"mood\": [Mood Rating from 1 to 10]}}"
Important: If you can't determine anything, return ONLY in the JSON format speciified above with "General" and a mood of 5
Important: The event_name is chosen from a list which is given in the pseudo JSON format given as follows
{{
  "event_name": select from {list_of_event_names} based on your analysis of the audio input
  "mood": Please analyze the audio input and select one of the task names. Then, rate the user's mood from 1 to 10, with 10 being the most happy. If the user is generally feeling happy or productive today and doesn't specify a task, select "General" as the event name.
}}
"""

print(PROMPT)

completion = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    modalities=["text"],
    audio={"voice": "alloy", "format": "wav"},
    
    messages=[
        {
            "role": "system",
            "content": "You are an assistant that analyzes audio and returns a JSON object with the task name and mood rating."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": PROMPT
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": encoded_audio,
                        "format": "wav"
                    }
                },
            ]
        },
    ]
)

print(completion.choices[0].message)

returned_json = completion.choices[0].message.content

print(f'returned_json =\n{returned_json}')

# Convert the string to a JSON object (Python dictionary)
parsed_json = json.loads(returned_json)

# Now parsed_json is a dictionary, and you can access its keys like a regular dictionary
print(f'parsed_json =\n{parsed_json}')

# Specify the filename
filename = "audio/output.json"

# Save parsed_json as a .json file
with open(filename, 'w') as json_file:
    json.dump(parsed_json, json_file, indent=4)
    

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
                    "text": "Respond positively trying to cheer the user up."
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

encoded_audio = completion.choices[0].message.audio.data

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
