# Public modules import
import threading

# Custom modules import
from constant import *
# from audio.mood import get_mood_json
import json
import os
import sys
import tkinter as tk
from GUI import TaskManagerApp 



def launch_gui(json_path):
    """
    Launch the task manager GUI
    """
    root = tk.Tk()
    app = TaskManagerApp(root, json_path)
    root.mainloop()
def main():
  
  # mood_json, mood_conversation_thread = get_mood_json()
  # print(f"main program has received the mood JSON =\n{mood_json}")

  #Assume here we obtain the final json file with all the needed info, at suggestion/suggestion.json(temperal)
  
  # If No need to wait for the sentence to be conpleted, comment out the following two line
  # mood_conversation_thread.join()
  # print("ChatGPT has finished saying! Thread has stopped")
  json_path = "suggestion/suggestion.json"
  launch_gui(json_path)
  
  

main()
