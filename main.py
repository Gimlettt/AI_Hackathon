# Public modules import

# Custom modules import
from constant import *
from audio.mood import mood_conversation
from audio.monitor import monitor_file_in_thread
import threading

def main():

  observer, monitor_thread = monitor_file_in_thread("output.json", directory="./audio/")
  mood_thread = threading.Thread(target=mood_conversation)
  mood_thread.start()
  monitor_thread.join()
  print("JSON file change detected! Thread has stopped")
  MOOD_EXTRACTION_COMPLETED, MOOD_JSON_CONVERSION_ERROR = False, False # Reset the monitor
  mood_thread.join()
  print("ChatGPT has finished saying! Thread has stopped")
#  mood_json = get_mood_json()
main()
