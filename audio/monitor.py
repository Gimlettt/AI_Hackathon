# This file monitors the output.json
# if it is updated, it allows the main function to continue to its next step

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import threading

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_to_watch, observer):
        self.file_to_watch = file_to_watch
        self.observer = observer

    def on_modified(self, event):
        if event.src_path.endswith(self.file_to_watch):
            print(f"File '{self.file_to_watch}' has been modified. Stopping watchdog...")
            MOOD_EXTRACTION_COMPLETED = True
            self.observer.stop()

def monitor_file_in_thread(file_path, directory="./audio/"):
    abs_directory = os.path.abspath(directory)
    abs_file_path = os.path.abspath(file_path)

    print(f"🔍 Watching directory: {abs_directory}")
    print(f"📄 Watching file: {abs_file_path}")
    
    observer = Observer()
    event_handler = FileChangeHandler(file_path, observer)
    
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    print(f"Watching {file_path} for changes...")

    def run_observer():
        try:
            while observer.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        print("Watchdog has stopped.")

    thread = threading.Thread(target=run_observer, daemon=True, name="Thread file monitoring")
    thread.start()
    return observer, thread  # Return the observer so you can manually stop it if needed

## Example Usage:
#observer = monitor_file_in_thread("output.json")
#
## Your main program can continue running here
#print("Main program is still running while watching the file...")
#
## To stop the observer manually later, call: observer.stop()
#while(True):
#  continue
