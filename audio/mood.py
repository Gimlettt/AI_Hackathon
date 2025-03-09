from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import json
import threading
import simpleaudio as sa
from pydub import AudioSegment
from io import BytesIO


# custom function
from audio.monitor import monitor_file_in_thread
from audio.record import record_voice
from constant import *

def Chat_GPT_mood_analysis(client, encoded_audio):
  # Get the absolute path of the current script (inside ./audio)
  current_dir = os.path.dirname(os.path.abspath(__file__))

  # Construct the path to the JSON file
  json_path = os.path.join(current_dir, "..", "quantify", "course_description.json")

  # Read the JSON file
  with open(json_path, "r", encoding="utf-8") as file:
      course_discription = json.load(file)

  # Extract the keys from the JSON object
  course_keys = list(course_discription.keys())
  
  course_keys.append("General")
  list_of_event_names = course_keys

#  list_of_event_names = ["3A1 coursework", "3F2 FTR", "3C5 lab report", "General", "Hackathon"]

  PROMPT = f"""
  You are an assistant analyzing a user's mood and what event they are referring to based on their audio input.
  Important: Return the results ONLY in JSON formats like this:\n\n{{\"event_name\": \"[Selected Task Name]\", \"mood\": [Mood Rating from 1 to 10]}}"
  Important: You can have multiple JSON answers, separated in comma, IF and ONLY IF you identify the user's mood to different events.
  Important: If you can't determine anything, return ONLY in the JSON format speciified above with "General" and a mood of 5
  Important: The event_name is chosen from a list which is given in the pseudo JSON format given as follows
  {{
    "event_name": select from {list_of_event_names} based on your analysis of the audio input
    "mood": Please analyze the audio input and select one of the task names. Then, rate the user's mood from 1 to 10, with 10 being the most happy. If the user is generally feeling happy or productive today and doesn't specify a task, select "General" as the event name.
  }}
  Important: The following is ONLY for multiple entries, the JSONs should be returned in a Python list. i.e. enclosed by [].
  [
    {{
      "event_name": first entry
      "mood": first entry
    }},{{
      "event_name": POTENTIAL second entry if you can identify one
      "mood": POTENTIAL second entry if you can identify one
    }},
    {{
      "event_name": POTENTIAL third entry if you can identify one, you may return more entries if you identify more events and related mood
      "mood": POTENTIAL third entry if you can identify one, you may return more entries if you identify more events and related mood
    }}
  ]
  IMPORTANT: You are also given some discription to the events, as follows
  {course_discription}
  """
  
  
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
  # Check if the string starts and ends with triple backticks
  if returned_json.startswith("```") and returned_json.endswith("```"):
    # Remove the leading and trailing triple backticks
    returned_json = returned_json[3:-3]

  print(f'returned_json =\n{returned_json}')
  try:
    # Try to parse the string to JSON (Python dictionary)
    parsed_json = json.loads(returned_json)
#    MOOD_JSON_CONVERSION_ERROR = False
  except json.JSONDecodeError:
    # If there's an error, return the error constant
    print("Error: MOOD_JSON_CONVERSION_ERROR, defaulting to the base case")
#    MOOD_JSON_CONVERSION_ERROR = True
    parsed_json = json.loads("""{"event_name": "General", "mood": 5}""")
  return parsed_json




def mood_conversation():
  # Record the user's message
  RECORDED_FILE_NAME = "audio/recorded_for_GPT.wav"
  record_voice(RECORD_SECONDS=DEFAULT_RECORDING_TIME, OUTPUT_FILENAME = RECORDED_FILE_NAME)
  
  # Read the audio file
  with open(RECORDED_FILE_NAME, 'rb') as audio_file:
      audio_input = audio_file.read()
      # Encode the binary data to base64
      encoded_audio = base64.b64encode(audio_input).decode('utf-8')

  # Load .env file from the root of the project to get the API
  load_dotenv()
  client = OpenAI(api_key = os.getenv('API_KEY'))
  
  # Get the JSON with mood score
  parsed_json = Chat_GPT_mood_analysis(client, encoded_audio)
  

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
                      "text": "Respond positively. Be natural and concise! Ideally no more than 10 seconds. Ask the user to clariify only if you're not sure of the user's mood."
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
  
  # If everything is done correctly
  return NO_EXCEPTION


# Listen to the user and returns a list of JSON rating the user's mood on each event
# mood_json is a list of json.
#   [
#     {
#       "event_name":
#       "mood":
#   ]
# mood_conversation_thread is the thread that controls the mood scoring and audio feedback
# the additioin of monitor_thread.join() in the code made sure that when mood_conversation_thread
# is returned, the program has moved on to "waiting for ChatGPT to respond"
def get_mood_json():
  observer, monitor_thread = monitor_file_in_thread("output.json", directory="./audio/")
  mood_conversation_thread = threading.Thread(target=mood_conversation, name="Thread mood conversation")
  mood_conversation_thread.start()
  monitor_thread.join()
  print("JSON file change detected! Thread has stopped")
  MOOD_EXTRACTION_COMPLETED, MOOD_JSON_CONVERSION_ERROR = False, False # Reset the monitor
  

  with open("audio/output.json", "r") as file:
    mood_json = json.load(file)
  
  if isinstance(mood_json, list):  # Check if it's already a list
    print("returned_json is already a Python list.")
  elif isinstance(mood_json, dict):  # Check if it's a single dictionary
    print("returned_json is a dictionary. Wrapping in a list.")
    mood_json = [mood_json]  # Wrap in a list for consistency
  
  print(f"Length of the JSON list is {len(mood_json)}")

  return mood_json, mood_conversation_thread
