import tkinter as tk
from tkinter import ttk, Frame, Label, font
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta
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
        
        # Create main frames
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
        
        # Top Row - Split into two columns: tasks and email summaries
        top_row = Frame(main_container, bg="#f0f0f0")
        top_row.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left column for tasks
        tasks_column = Frame(top_row, bg="white", width=500)
        tasks_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tasks_column.pack_propagate(False)  # Prevent shrinking
        
        # Header for tasks
        task_header = Label(tasks_column, text="Would you like to do?", font=("Arial", 14, "bold"), bg="white", anchor="w")
        task_header.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame for tasks
        self.tasks_frame = Frame(tasks_column, bg="white")
        self.tasks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Right column for email summaries
        email_column = Frame(top_row, bg="white", width=500)
        email_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        email_column.pack_propagate(False)  # Prevent shrinking
        
        # Header for email summaries
        email_header = Label(email_column, text="Email Summary", font=("Arial", 14, "bold"), bg="white", anchor="w")
        email_header.pack(fill=tk.X, padx=10, pady=10)
        
        # Create frames for categories in the email column
        self.category1_frame = Frame(email_column, bg="white")
        self.category1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        category1_label = Label(self.category1_frame, text="Category 1", font=("Arial", 12, "bold"), bg="white", anchor="w")
        category1_label.pack(fill=tk.X)
        
        self.category1_emails_frame = Frame(self.category1_frame, bg="white")
        self.category1_emails_frame.pack(fill=tk.X, padx=20)
        
        self.category2_frame = Frame(email_column, bg="white")
        self.category2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        category2_label = Label(self.category2_frame, text="Category 2", font=("Arial", 12, "bold"), bg="white", anchor="w")
        category2_label.pack(fill=tk.X)
        
        self.category2_emails_frame = Frame(self.category2_frame, bg="white")
        self.category2_emails_frame.pack(fill=tk.X, padx=20)
        
        # Bottom frame for Gantt chart
        bottom_frame = Frame(main_container, bg="white", height=200)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        bottom_frame.pack_propagate(False)  # Prevent shrinking
        
        # Create Gantt chart
        self.create_gantt_chart(bottom_frame)
    
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
        
        # Populate email summaries for Category 1
        email1_label = Label(self.category1_emails_frame, text="email summary 1", font=("Arial", 10), bg="white", anchor="w")
        email1_label.pack(fill=tk.X, pady=2)
        
        email2_label = Label(self.category1_emails_frame, text="email summary 2", font=("Arial", 10), bg="white", anchor="w")
        email2_label.pack(fill=tk.X, pady=2)
        
        # Populate email summaries for Category 2
        email1_label = Label(self.category2_emails_frame, text="email summary 1", font=("Arial", 10), bg="white", anchor="w")
        email1_label.pack(fill=tk.X, pady=2)
        
        email2_label = Label(self.category2_emails_frame, text="email summary 2", font=("Arial", 10), bg="white", anchor="w")
        email2_label.pack(fill=tk.X, pady=2)
    
    def create_gantt_chart(self, parent_frame):
        # Create figure for the Gantt chart
        fig, ax = plt.subplots(figsize=(10, 3), dpi=100)
        fig.patch.set_facecolor('white')
        
        # Sample data for Gantt chart
        tasks = [task["assignment_name"].split('.')[0] for task in self.top_tasks]
        
        # Generate random start dates spread over next 10 days
        now = datetime.now()
        start_dates = [now + timedelta(days=i*2) for i in range(len(tasks))]
        
        # Generate random durations between 1 and 5 days
        durations = [np.random.randint(1, 6) for _ in range(len(tasks))]
        
        # Define colors for tasks
        colors = ['red', 'blue', 'green']
        
        # Create the Gantt chart with simple colored bars
        for i, (task, start_date, duration) in enumerate(zip(tasks, start_dates, durations)):
            # Draw the bar
            ax.barh(
                i, 
                duration, 
                left=np.datetime64(start_date), 
                height=0.5, 
                align='center',
                color=colors[i % len(colors)],
                edgecolor='black',
                linewidth=1
            )
            
            # Add task label to the left of the bar
            ax.text(
                np.datetime64(start_date) - np.timedelta64(1, 'D'), 
                i, 
                task, 
                ha='right', 
                va='center',
                fontsize=9
            )
            
            # Add duration text on the bar
            ax.text(
                np.datetime64(start_date) + np.timedelta64(int(duration/2), 'D'),
                i,
                f"{duration} days",
                ha='center',
                va='center',
                fontsize=8,
                color='white' if i != 2 else 'black',  # Ensure text is visible against bar color
                fontweight='bold'
            )
        
        # Format the chart
        ax.set_yticks([])
        ax.set_title('Task Timeline', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Format x-axis to show dates
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d'))
        
        # Add some padding to the left to make room for task names
        date_min = np.datetime64(now - timedelta(days=3))
        date_max = np.datetime64(now + timedelta(days=max(durations) + 5))
        ax.set_xlim(left=date_min, right=date_max)
        
        # Remove chart border
        for spine in ['top', 'right', 'left']:
            ax.spines[spine].set_visible(False)
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed the chart in tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Draw the canvas
        canvas.draw()

def run_gui(json_file=None):
    """
    Run the Task Manager GUI with the specified JSON file.
    
    Args:
        json_file (str, optional): Path to the JSON file containing task data.
                                   Defaults to None (which will use the default path).
    """
    root = tk.Tk()
    app = TaskManagerApp(root, json_file)
    root.mainloop()

# If the script is run directly, check for command line arguments
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the first command line argument as the JSON file path
        json_file = sys.argv[1]
        run_gui(json_file)
    else:
        # No command line argument, use default
        run_gui()