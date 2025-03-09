import tkinter as tk
from tkinter import Frame, Label, Button
import json
import sys
import os

class TaskManagerApp:
    def __init__(self, root, json_file=None, explanation_file=None):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        
        # Use provided JSON file paths or defaults
        self.json_file = json_file or "suggestion/suggestion.json"
        self.explanation_file = explanation_file or "suggestion/suggestion_output.json"
        
        # Load task data
        self.tasks = self.load_tasks(self.json_file)
        # Sort tasks by urgency (highest first)
        self.tasks.sort(key=lambda x: x["urgency"], reverse=True)
        # Get top 3 urgent tasks
        self.top_tasks = self.tasks[:3]
        # Load explanation data
        self.explanation = self.load_explanation(self.explanation_file)
        
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

    def load_explanation(self, filename):
        try:
            with open(filename, 'r') as file:
                print(f"Successfully loaded explanation from {filename}")
                return json.load(file)
        except Exception as e:
            print(f"Error loading explanation JSON {filename}: {e}")
            return {}
    
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
        # Populate top 3 urgent tasks and display explanation for each
        for i, task in enumerate(self.top_tasks):
            rank = i + 1
            task_frame = Frame(self.tasks_frame, bg="white", bd=1, relief=tk.RIDGE, padx=5, pady=5)
            task_frame.pack(fill=tk.X, pady=5)
            
            # Assignment label
            task_label = Label(
                task_frame, 
                text=f"{rank}. {task['assignment_name']}", 
                font=("Arial", 11, "bold"), 
                bg="white", 
                anchor="w"
            )
            task_label.pack(fill=tk.X, side=tk.LEFT)
            
            # Explanation label (if available)
            key = f"reason_rank_{rank}"
            explanation_text = self.explanation.get(key, "No explanation provided.")
            explanation_label = Label(
                task_frame,
                text=explanation_text,
                font=("Arial", 10),
                bg="white",
                wraplength=600,
                justify="left"
            )
            explanation_label.pack(fill=tk.X, pady=(2, 0))
            
            # Add a button to make the assignment clickable
            action_button = Button(
                task_frame,
                text="Select",
                command=lambda r=rank: self.handle_click(r)
            )
            action_button.pack(side=tk.RIGHT, padx=5)
    
    def handle_click(self, rank):
        print(f"Assignment {rank} clicked")

def run_gui(json_file=None, explanation_file=None):
    root = tk.Tk()
    app = TaskManagerApp(root, json_file, explanation_file)
    root.mainloop()

if __name__ == "__main__":
    # Optionally, pass JSON file paths from command-line arguments
    json_file = sys.argv[1] if len(sys.argv) > 1 else None
    explanation_file = sys.argv[2] if len(sys.argv) > 2 else None
    run_gui(json_file, explanation_file)
