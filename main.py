# Public modules import
import threading

# Custom modules import
from constant import *
from audio.mood import get_mood_json

def main():
  
  mood_json, mood_conversation_thread = get_mood_json()
  print(f"main program has received the mood JSON =\n{mood_json}")
  
  # If No need to wait for the sentence to be conpleted, comment out the following two line
  mood_conversation_thread.join()
  print("ChatGPT has finished saying! Thread has stopped")
  

main()
