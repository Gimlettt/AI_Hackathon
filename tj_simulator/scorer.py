import json
import os
from datetime import datetime, timedelta
import math


# Define global working hours (9:00-19:00)
WORK_START_HOUR = 9
WORK_END_HOUR = 19
# Define fixed deadline time
DEADLINE_HOUR = 19


class TaskScheduler:
    def __init__(self, tasks_data=None, start_date=None, output_dir="score_output_test"):
        """
        Initialize the task scheduler with tasks data and start date
        
        Parameters:
        tasks_data (list): List of task dictionaries
        start_date (datetime): Starting date and time for the scheduler
        output_dir (str): Directory to save task snapshots
        """
        self.start_date = start_date if start_date else datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        self.current_date = self.start_date
        self.output_dir = output_dir
        self.work_start_hour = WORK_START_HOUR
        self.work_end_hour = WORK_END_HOUR
        self.deadline_hour = DEADLINE_HOUR
        
        # Initialize tasks if provided
        if tasks_data:
            self.tasks = self.initialize_tasks(tasks_data)
        else:
            self.tasks = []
            
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
    def initialize_tasks(self, tasks_data):
        """
        Initialize tasks with deadlines and completed work
        
        Parameters:
        tasks_data (list): List of task dictionaries
        
        Returns:
        list: Processed task list with additional fields
        """
        tasks = []
        for task in tasks_data:
            task_copy = task.copy()
            # Parse deadline
            month, day = map(int, task_copy['DDL'].split('/'))
            task_copy['deadline'] = datetime(self.start_date.year, month, day, self.deadline_hour, 0)
            task_copy['completed_work'] = 0  # Initialize completed work time
            tasks.append(task_copy)
        return tasks
    
    def load_tasks_from_json(self, filename):
        """
        Load tasks from a JSON file
        
        Parameters:
        filename (str): Path to the JSON file
        """
        with open(filename, 'r') as f:
            tasks_data = json.load(f)
        self.tasks = self.initialize_tasks(tasks_data)
        return len(self.tasks)
    
    def is_working_hours(self, dt):
        """
        Check if a datetime is during working hours
        
        Parameters:
        dt (datetime): Datetime to check
        
        Returns:
        bool: True if during working hours, False otherwise
        """
        return self.work_start_hour <= dt.hour < self.work_end_hour
    
    def get_next_working_time(self, dt):
        """
        Get the next working time from a given datetime
        
        Parameters:
        dt (datetime): Current datetime
        
        Returns:
        datetime: Next working time
        """
        # If current time is later than work end time, advance to next day's work start time
        if dt.hour >= self.work_end_hour:
            next_day = dt + timedelta(days=1)
            return datetime(next_day.year, next_day.month, next_day.day, self.work_start_hour, 0)
        # If current time is earlier than work start time, advance to current day's work start time
        elif dt.hour < self.work_start_hour:
            return datetime(dt.year, dt.month, dt.day, self.work_start_hour, 0)
        # Already during working hours
        return dt
    
    def save_tasks_snapshot(self, current_time):
        """
        Save current task status to a JSON file
        
        Parameters:
        current_time (datetime): Current time for the snapshot
        
        Returns:
        str: Path to the saved snapshot file
        """
        # Create filename with timestamp
        timestamp = current_time.strftime("%Y%m%d_%H%M")
        filename = os.path.join(self.output_dir, f"tasks_{timestamp}.json")
        
        # Create serializable copy of tasks
        serializable_tasks = []
        for task in self.tasks:
            task_copy = task.copy()
            # Convert datetime objects to strings
            if 'deadline' in task_copy:
                task_copy['deadline'] = task_copy['deadline'].strftime("%Y-%m-%d %H:%M")
            serializable_tasks.append(task_copy)
        
        # Save tasks to JSON file
        with open(filename, 'w') as f:
            json.dump(serializable_tasks, f, indent=4)
        
        return filename
    
    def calculate_available_working_hours(self, start_date, deadline):
        """
        Calculate available working hours before a deadline
        
        Parameters:
        start_date (datetime): Starting datetime
        deadline (datetime): Deadline datetime
        
        Returns:
        float: Available working hours
        """
        # Daily work hours
        daily_work_hours = self.work_end_hour - self.work_start_hour
        
        # Start date
        current_date = start_date
        total_hours = 0
        
        # Get date part of deadline (without time)
        deadline_day = deadline.date()
        
        # If start date is already after deadline, no time available
        if current_date.date() > deadline_day:
            return 0
            
        # Handle start day (if during working hours)
        if current_date.date() == deadline_day:
            # If current date is deadline day, can only work until deadline time
            end_hour = min(self.deadline_hour, self.work_end_hour)
            start_hour = max(current_date.hour, self.work_start_hour)
            # If start time is already past end time, no time available
            if start_hour >= end_hour:
                return 0
            hours_today = end_hour - start_hour
            total_hours += hours_today
            return total_hours
        else:
            # If not deadline day, can use extended work time
            if current_date.hour < self.work_end_hour:
                # Calculate remaining work time today
                start_hour = max(current_date.hour, self.work_start_hour)
                hours_today = self.work_end_hour - start_hour
                total_hours += hours_today
        
        # Advance to next day
        current_date = datetime(current_date.year, current_date.month, current_date.day, 0, 0) + timedelta(days=1)
        
        # Handle middle days (full work days)
        while current_date.date() < deadline_day:
            total_hours += daily_work_hours
            current_date += timedelta(days=1)
        
        # Handle deadline day (if any)
        if current_date.date() == deadline_day:
            # Can only work until DEADLINE_HOUR (19:00) on deadline day
            hours_deadline_day = max(0, self.deadline_hour - self.work_start_hour)
            total_hours += hours_deadline_day
        
        return total_hours
    
    def check_time_sufficiency(self, tasks, current_date):
        """
        Check if there's enough working time to complete specified tasks
        
        Parameters:
        tasks (list): List of tasks to check
        current_date (datetime): Current datetime
        
        Returns:
        list: List of tuples with insufficient deadlines (deadline, required_hours, available_hours)
        """
        # Sort tasks by deadline
        sorted_tasks = sorted(tasks, key=lambda x: x['deadline'])
        
        # Group tasks by deadline
        tasks_by_deadline = {}
        for task in sorted_tasks:
            deadline_str = task['deadline'].strftime('%Y-%m-%d')
            if deadline_str not in tasks_by_deadline:
                tasks_by_deadline[deadline_str] = []
            tasks_by_deadline[deadline_str].append(task)
        
        # Check each deadline
        insufficient_deadlines = []
        accumulated_tasks = []
        
        for deadline_str, deadline_tasks in sorted(tasks_by_deadline.items()):
            # Add current deadline's tasks to accumulated task list
            accumulated_tasks.extend(deadline_tasks)
            
            # Get datetime object for current deadline
            current_deadline = deadline_tasks[0]['deadline']
            
            # Calculate available working hours before deadline
            available_hours = self.calculate_available_working_hours(current_date, current_deadline)
            
            # Calculate total work time needed (all tasks with deadlines before or equal to current deadline)
            required_hours = sum(float(task['duration']) - task.get('completed_work', 0) for task in accumulated_tasks)
            
            if required_hours > available_hours:
                insufficient_deadlines.append((current_deadline, required_hours, available_hours))
        
        return insufficient_deadlines
    
    def adjust_work_end_time(self, insufficient_deadlines, current_date):
        """
        Calculate adjusted work end time based on insufficient deadlines
        
        Parameters:
        insufficient_deadlines (list): List of insufficient deadlines
        current_date (datetime): Current datetime
        
        Returns:
        int: New work end hour
        """
        max_additional_hours_needed = 0
        
        for deadline, required, available in insufficient_deadlines:
            # Calculate time shortage
            shortage = required - available
            
            # Calculate working days from current date to day before deadline (not including deadline day)
            current_day = current_date.date()
            deadline_day = deadline.date()
            working_days = 0
            
            check_date = current_day
            while check_date < deadline_day:  # Not including deadline_day
                # For simplicity, assume all dates are working days
                working_days += 1
                check_date += timedelta(days=1)
            
            if working_days <= 0:
                # If already deadline day, cannot adjust work time
                continue
            
            # Additional hours needed per day
            additional_hours_per_day = math.ceil(shortage / working_days)
            max_additional_hours_needed = max(max_additional_hours_needed, additional_hours_per_day)
        
        # Ensure additional time is a multiple of 2 (convenient for 2-hour work sessions)
        if max_additional_hours_needed % 2 != 0:
            max_additional_hours_needed += 1
        
        # Ensure new end time doesn't exceed midnight
        new_end_hour = min(24, self.work_end_hour + max_additional_hours_needed)
        
        return new_end_hour
    
    def update_working_hours(self, new_end_hour):
        """
        Update working hours end time
        
        Parameters:
        new_end_hour (int): New work end hour
        """
        self.work_end_hour = new_end_hour
        return self.work_end_hour
    
    def recalculate_all_tasks(self, current_date):
        """
        Recalculate available time and urgency for all tasks
        
        Parameters:
        current_date (datetime): Current datetime
        """
        for task in self.tasks:
            if current_date < task['deadline']:
                # Calculate effective work time before deadline (only considering hours during work time)
                time_to_deadline = self.calculate_available_working_hours(current_date, task['deadline'])
                task['time_to_deadline'] = time_to_deadline
                
                # Update urgency
                duration = float(task['duration'])
                duration_left = max(0, duration - task.get('completed_work', 0))
                
                if time_to_deadline <= 0:
                    urgency = 100  # Past deadline
                elif duration_left <= 0:
                    urgency = 0    # Task completed
                else:
                    # New urgency formula: 100 * (duration_left / (time_to_deadline + duration_left)) * (1 + duration_left)
                    urgency = 100 * (duration_left / (time_to_deadline + duration_left)) * (1 + 1/duration_left)
                
                task['urgency'] = urgency  # Keep as float for more precise sorting
                task['duration_left'] = duration_left
    
    def check_and_adjust_working_hours(self, current_date):
        """
        Check and adjust working hours if needed
        
        Parameters:
        current_date (datetime): Current datetime
        
        Returns:
        bool: True if adjustment was made, False otherwise
        """
        # Filter future tasks (deadlines after current date and not completed)
        future_tasks = [task for task in self.tasks if task['deadline'] > current_date and 
                        float(task['duration']) - task.get('completed_work', 0) > 0]
        
        if not future_tasks:
            # If no future tasks, restore standard working hours
            self.update_working_hours(19)
            return True
        
        # Save current work end time to check if standard work time is enough
        current_work_end_hour = self.work_end_hour
        
        # Temporarily set work time to standard (19:00) for calculation
        temp_work_end_hour = 19
        self.update_working_hours(temp_work_end_hour)
        
        # Check if standard work time is enough for all future tasks
        insufficient_deadlines = self.check_time_sufficiency(future_tasks, current_date)
        
        if not insufficient_deadlines:
            # If standard work time is enough, keep 19:00 end
            return False
        else:
            # If standard work time is not enough, calculate how much extension is needed
            # Restore previous work end time for recalculation
            self.update_working_hours(current_work_end_hour)
            
            # Recalculate if time adjustment is needed under current conditions
            insufficient_deadlines = self.check_time_sufficiency(future_tasks, current_date)
            
            if not insufficient_deadlines:
                # If current time is enough (may have been extended), keep it
                return False
            
            # Calculate needed new end time
            new_end_hour = self.adjust_work_end_time(insufficient_deadlines, current_date)
            
            # Ensure new end time is not earlier than current end time (unless can return to 19:00)
            if 19 < new_end_hour < current_work_end_hour:
                new_end_hour = current_work_end_hour
                return False
            
            # Update work hours
            self.update_working_hours(new_end_hour)
            return True
    
    def get_top_urgent_tasks(self, top_n=3):
        """
        Get the top N most urgent active tasks based on weighted score of urgency, importance and mood
        
        Parameters:
        top_n (int): Number of top urgent tasks to return
        
        Returns:
        list: List of tuples (task_index, task_dict) or empty list if no active tasks
        """
        active_tasks = []
        for i, task in enumerate(self.tasks):
            # If current time is before deadline and task is not completed
            if (self.current_date < task['deadline'] and 
                float(task['duration']) - task.get('completed_work', 0) > 0):
                active_tasks.append((i, task))
        
        if not active_tasks:
            return []
            
        # Calculate weighted score for each task
        for i, task in active_tasks:
            urgency = task['urgency']
            importance = float(task.get('importance', 5))  # Default to 5 if not provided
            mood = float(task.get('mood', 5))  # Default to 5 if not provided
            
            # Calculate weighted score (adjust weights as needed)
            weighted_score = 0.5 * urgency + 0.3 * importance + 0.2 * mood
            task['weighted_score'] = weighted_score
        
        # Sort by weighted score and return top N
        active_tasks.sort(key=lambda x: x[1]['weighted_score'], reverse=True)
        return active_tasks[:min(top_n, len(active_tasks))]
    
    def get_most_urgent_task(self):
        """
        Get the most urgent active task
        
        Returns:
        tuple: (task_index, task_dict) or (None, None) if no active tasks
        """
        top_tasks = self.get_top_urgent_tasks(1)
        if not top_tasks:
            return None, None
        return top_tasks[0]
    
    def work_on_task(self, task_index, hours=2):
        """
        Work on a task for specified hours
        
        Parameters:
        task_index (int): Index of the task in the tasks list
        hours (float): Hours to work on the task
        
        Returns:
        dict: Updated task
        """
        if task_index is None or task_index >= len(self.tasks):
            return None
            
        task = self.tasks[task_index]
        task['completed_work'] = task.get('completed_work', 0) + hours
        
        # Update status after processing
        duration = float(task['duration'])
        time_to_deadline = self.calculate_available_working_hours(self.current_date, task['deadline'])
        duration_left = max(0, duration - task['completed_work'])
        
        # Update task fields
        task['duration_left'] = duration_left
        task['time_to_deadline'] = time_to_deadline
        
        # Recalculate urgency with new formula
        if time_to_deadline <= 0:
            urgency = 100  # Past deadline
        elif duration_left <= 0:
            urgency = 0    # Task completed
        else:
            # New urgency formula: 100 * (duration_left / (time_to_deadline + duration_left)) * (1 + duration_left)
            urgency = 100 * (duration_left / (time_to_deadline + duration_left)) * (1 + 1/duration_left)
        
        task['urgency'] = urgency
        
        return task
    
    def advance_time(self, hours=2):
        """
        Advance the current time by specified hours
        
        Parameters:
        hours (float): Hours to advance
        
        Returns:
        datetime: New current time
        """
        old_date = self.current_date
        self.current_date += timedelta(hours=hours)
        
        # If outside working hours, adjust to next working time
        if not self.is_working_hours(self.current_date):
            self.current_date = self.get_next_working_time(self.current_date)
        
        return self.current_date
    
    def save_results(self, filename='output.json'):
        """
        Save final results to a JSON file
        
        Parameters:
        filename (str): Output file name
        """
        final_tasks = []
        for task in self.tasks:
            task_copy = task.copy()
            # Convert datetime objects to strings
            if 'deadline' in task_copy:
                task_copy['deadline'] = task_copy['deadline'].strftime("%Y-%m-%d %H:%M")
            final_tasks.append(task_copy)
        
        with open(filename, 'w') as f:
            json.dump(final_tasks, f, indent=4)
        
        return filename
    
    def get_task_status(self):
        """
        Get status of all tasks
        
        Returns:
        list: List of task status dictionaries
        """
        status_list = []
        for i, task in enumerate(self.tasks):
            duration = float(task['duration'])
            completed_work = task.get('completed_work', 0)
            duration_left = task.get('duration_left', max(0, duration - completed_work))
            urgency = task.get('urgency', 0)
            
            status = {
                'index': i,
                'name': task.get('name', task.get('assignment_name', 'Unnamed Task')),
                'duration': duration,
                'completed_work': completed_work,
                'duration_left': duration_left,
                'urgency': urgency,
                'deadline': task['deadline'].strftime('%Y-%m-%d %H:%M'),
                'is_completed': duration_left <= 0
            }
            status_list.append(status)
        
        return status_list
    
    def run_simulation(self):
        """
        Run the full task scheduling simulation
        """
        continue_simulation = True
        first_iteration = True
        
        # Ensure current time is within working hours
        self.current_date = self.get_next_working_time(self.current_date)
        print(f"Adjusted start time: {self.current_date.strftime('%Y-%m-%d %H:%M')}")
        
        print("\nProgram starting, work schedule will be checked at the first 9:00 AM...")
        
        while continue_simulation:
            # Check if during working hours
            if self.is_working_hours(self.current_date):
                print(f"\nCurrent time point: {self.current_date.strftime('%Y-%m-%d %H:%M')}")
                
                # Check if it's 9:00 AM of a new day (adjust work hours at 9:00 AM every day)
                if self.current_date.hour == 9 and self.current_date.minute == 0:
                    print("\nNew day begins, checking today's work hour arrangement...")
                    
                    # Filter future tasks (deadlines after current date and not completed)
                    future_tasks = [task for task in self.tasks if task['deadline'] > self.current_date and 
                                    float(task['duration']) - task.get('completed_work', 0) > 0]
                    
                    if not future_tasks:
                        print("No tasks to complete, using standard work hours (9:00-19:00)")
                        self.update_working_hours(19)
                    else:
                        # Save current work end time
                        current_end_hour = self.work_end_hour
                        
                        # Temporarily set to standard work hours (9:00-19:00)
                        self.update_working_hours(19)
                        print("Checking if all tasks can be completed within standard work hours (9:00-19:00)...")
                        
                        # Check if standard work hours are sufficient
                        insufficient_deadlines = self.check_time_sufficiency(future_tasks, self.current_date)
                        
                        if not insufficient_deadlines:
                            print("Starting today, can restore standard work hours (9:00-19:00), task progress is good")
                            # Already set to 19:00, no need to change
                        else:
                            print("Standard work hours are not sufficient to complete all tasks, need to extend work hours")
                            # Calculate needed new end time
                            new_end_hour = self.adjust_work_end_time(insufficient_deadlines, self.current_date)
                            self.update_working_hours(new_end_hour)
                            print(f"Work hours adjusted to {self.work_start_hour}:00-{self.work_end_hour}:00")
                    
                    # Recalculate all tasks' time (because work hours may have changed)
                    self.recalculate_all_tasks(self.current_date)
                
                # Update status and urgency of all uncompleted tasks
                self.recalculate_all_tasks(self.current_date)
                
                # Get top 3 most urgent tasks
                top_urgent_tasks = self.get_top_urgent_tasks(3)
                
                # If no active tasks, end simulation
                if not top_urgent_tasks:
                    print("All tasks completed or deadline reached, ending simulation.")
                    break
                
                # Display status of all tasks
                print("\nCurrent task status:")
                for task_status in self.get_task_status():
                    if not task_status['is_completed']:
                        i = task_status['index']
                        print(f"Task {i+1}: {task_status['name']}")
                        print(f"  Accumulated work time: {task_status['completed_work']} hours")
                        print(f"  Remaining work time: {task_status['duration_left']} hours")
                        print(f"  Effective work time before deadline: {self.tasks[i].get('time_to_deadline', 0):.2f} hours")
                        print(f"  Urgency: {task_status['urgency']:.2f}%")
                
                # Save current status to JSON file
                snapshot_file = self.save_tasks_snapshot(self.current_date)
                print(f"Saved task snapshot to: {snapshot_file}")
                
                # Display top 3 suggestions based on weighted score
                print("\nTop 3 suggested tasks based on weighted score:")
                for i, (task_idx, task) in enumerate(top_urgent_tasks):
                    print(f"{i+1}. Task {task_idx+1}: {task.get('name', task.get('assignment_name', 'Unnamed Task'))}")
                    print(f"   Weighted Score: {task['weighted_score']:.2f}")
                    print(f"   Urgency: {task['urgency']:.2f}%")
                    print(f"   Importance: {task.get('importance', 5)}")
                    print(f"   Mood: {task.get('mood', 5)}")
                    print(f"   Remaining work: {task.get('duration_left', 0)} hours")
                    print(f"   Deadline: {task['deadline'].strftime('%Y-%m-%d %H:%M')}")
                
                if first_iteration:
                    # First iteration, ask user to choose which task to work on
                    print("\nWhich task would you like to work on for the next 2 hours? (Enter 1-3, or press Enter for the most urgent):")
                    user_choice = input().strip()
                    
                    # Default to most urgent if no input
                    selected_idx = 0
                    if user_choice and user_choice.isdigit():
                        choice = int(user_choice) - 1
                        if 0 <= choice < len(top_urgent_tasks):
                            selected_idx = choice
                    
                    # Get selected task
                    task_idx, selected_task = top_urgent_tasks[selected_idx]
                    
                    # Work on selected task
                    self.work_on_task(task_idx, 2)
                    
                    print(f"\nWill begin processing task: {selected_task.get('name', selected_task.get('assignment_name', 'Unnamed Task'))}")
                    print(f"\nCompleted 2 hours of work on this task from 09:00-11:00")
                    print(f"  Accumulated work time: {selected_task['completed_work']} hours")
                    print(f"  Remaining work time: {selected_task['duration_left']} hours")
                    print(f"  Effective work time before deadline: {selected_task['time_to_deadline']:.2f} hours")
                    first_iteration = False
                else:
                    # Normal processing - ask user to choose which task to work on
                    print("\nWhich task would you like to work on for the next 2 hours? (Enter 1-3, or press Enter for the most urgent):")
                    user_choice = input().strip()
                    
                    # Default to most urgent if no input
                    selected_idx = 0
                    if user_choice and user_choice.isdigit():
                        choice = int(user_choice) - 1
                        if 0 <= choice < len(top_urgent_tasks):
                            selected_idx = choice
                    
                    # Get selected task
                    task_idx, selected_task = top_urgent_tasks[selected_idx]
                    
                    # Work on selected task
                    self.work_on_task(task_idx, 2)
                    
                    print(f"\nCompleted 2 hours of work on task: {selected_task.get('name', selected_task.get('assignment_name', 'Unnamed Task'))}")
                    print(f"  Accumulated work time: {selected_task['completed_work']} hours")
                    print(f"  Remaining work time: {selected_task['duration_left']} hours")
                    print(f"  Effective work time before deadline: {selected_task['time_to_deadline']:.2f} hours")
                
                # Ask user whether to continue
                # print(f"\nCurrent time: {self.current_date.strftime('%Y-%m-%d %H:%M')}")
                if first_iteration:
                    print("Ready to start work. Press Enter to continue, enter 'stop' to stop...")
                else:
                    print("Two hours have passed. Press Enter to continue, enter 'stop' to stop...")
                user_input = input()
                
                if user_input.lower() == 'stop':
                    print("User chose to stop")
                    continue_simulation = False
                    break
                
                # Advance 2 hours
                old_date = self.current_date
                self.advance_time(2)
                print(f"Time advances: {old_date.strftime('%H:%M')} -> {self.current_date.strftime('%H:%M')}")
                
                # Print separator
                print("\n" + "#" * 50)
            else:
                # Not during working hours, skip to next working time
                old_date = self.current_date
                self.current_date = self.get_next_working_time(self.current_date)
                print(f"Not during working hours, adjusted to: {old_date.strftime('%Y-%m-%d %H:%M')} -> {self.current_date.strftime('%Y-%m-%d %H:%M')}")
                
                # Print separator
                print("\n" + "#" * 50)
        
        # Display final results for all tasks
        print("\nFinal results for all tasks:")
        for task_status in self.get_task_status():
            i = task_status['index']
            print(f"\nTask {i+1}:")
            print(f"Task name: {task_status['name']}")
            print(f"Duration: {task_status['duration']} hours")
            print(f"Completed time: {task_status['completed_work']} hours")
            print(f"Remaining work time: {task_status['duration_left']} hours")
            print(f"Urgency: {task_status['urgency']:.2f}%")
            print(f"Deadline: {task_status['deadline']}")
        
        # Save final results to output.json
        output_file = self.save_results('output.json')
        print(f"\nAll tasks processed, final results saved to {output_file}")
        
        return self.get_task_status()


# Example usage
if __name__ == "__main__":
    # Create a scheduler with start date
    start_date = datetime(2025, 1, 1, 9, 00)
    scheduler = TaskScheduler(start_date=start_date)
    
    print(f"Initial time: {start_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Load tasks from JSON file
    num_tasks = scheduler.load_tasks_from_json('tj_simulator/eval_example_from_max.json')
    print(f"Loaded {num_tasks} tasks")
    
    # Run the simulation
    scheduler.run_simulation()