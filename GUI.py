import tkinter as tk
from tkinter import Frame, Label
import json
import sys
import os

class TaskManagerApp:
    def __init__(self, root, json_file=None):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        
        # Use provided JSON file path or default
        self.json_file = json_file or "suggestion/suggestion.json"
        
        # Load task data
        self.tasks = self.load_tasks(self.json_file)
        
        # Sort tasks by urgency (highest first)
        self.tasks.sort(key=lambda x: x["urgency"], reverse=True)
        
        # Get top 3 urgent tasks
        self.top_tasks = self.tasks[:3]
        
        # Create main frames (only the top left tasks section)
        self.create_layout()
        
        # Populate with data
        self.populate_data()
        
    def load_tasks(self, filename):
        try:
            with open(filename, 'r') as file:
                print(f"Successfully loaded data from {filename}")
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON file {filename}: {e}")
            raise
    
    def create_layout(self):
        # Main container
        main_container = Frame(self.root, bg="#f0f0f0")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Only top left section for tasks
        tasks_column = Frame(main_container, bg="white")
        tasks_column.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tasks_column.pack_propagate(False)
        
        # Header for tasks
        task_header = Label(tasks_column, text="Would you like to do?", font=("Arial", 14, "bold"), bg="white", anchor="w")
        task_header.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame for tasks list
        self.tasks_frame = Frame(tasks_column, bg="white")
        self.tasks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def populate_data(self):
        # Populate top 3 urgent tasks
        for i, task in enumerate(self.top_tasks):
            task_number = i + 1
            task_frame = Frame(self.tasks_frame, bg="white")
            task_frame.pack(fill=tk.X, pady=2)
            
            task_label = Label(
                task_frame, 
                text=f"{task_number}. {task['assignment_name']}", 
                font=("Arial", 11), 
                bg="white", 
                anchor="w",
                padx=5
            )
            task_label.pack(side=tk.LEFT)
    
def run_gui(json_file=None):
    root = tk.Tk()
    app = TaskManagerApp(root, json_file)
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        run_gui(json_file)
    else:
        run_gui()
