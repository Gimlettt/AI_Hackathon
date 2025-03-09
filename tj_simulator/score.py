import json
import os
from datetime import datetime, timedelta
import math


current_date = datetime(2025, 1, 1, 9, 00)
print(f"Initial time: {current_date.strftime('%Y-%m-%d %H:%M')}")

# Load JSON input
with open('input.json', 'r') as f:
    tasks = json.load(f)
print(f"Loaded {len(tasks)} tasks")

# Define global working hours (9:00-19:00)
WORK_START_HOUR = 9
WORK_END_HOUR = 19
# Define fixed deadline time
DEADLINE_HOUR = 19

# Check if time is during working hours
def is_working_hours(dt):
    return WORK_START_HOUR <= dt.hour < WORK_END_HOUR

# Get next working time
def get_next_working_time(dt):
    # If current time is later than work end time, advance to next day's work start time
    if dt.hour >= WORK_END_HOUR:
        next_day = dt + timedelta(days=1)
        return datetime(next_day.year, next_day.month, next_day.day, WORK_START_HOUR, 0)
    # If current time is earlier than work start time, advance to current day's work start time
    elif dt.hour < WORK_START_HOUR:
        return datetime(dt.year, dt.month, dt.day, WORK_START_HOUR, 0)
    # Already during working hours
    return dt

# Ensure output directory exists
output_dir = "score_output_test"
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory: {os.path.abspath(output_dir)}")

# Save current task status to JSON file
def save_tasks_snapshot(tasks, current_time):
    # Create filename with timestamp
    timestamp = current_time.strftime("%Y%m%d_%H%M")
    filename = os.path.join(output_dir, f"tasks_{timestamp}.json")
    
    # Create serializable copy of tasks
    serializable_tasks = []
    for task in tasks:
        task_copy = task.copy()
        # Convert datetime objects to strings
        if 'deadline' in task_copy:
            task_copy['deadline'] = task_copy['deadline'].strftime("%Y-%m-%d %H:%M")
        serializable_tasks.append(task_copy)
    
    # Save tasks to JSON file
    with open(filename, 'w') as f:
        json.dump(serializable_tasks, f, indent=4)
    
    print(f"Saved task snapshot to: {filename}")

# Parse all tasks' deadlines, fixed to 19:00 on the specified day (not affected by work time adjustments)
for task in tasks:
    month, day = map(int, task['DDL'].split('/'))
    task['deadline'] = datetime(2025, month, day, DEADLINE_HOUR, 0)  # Deadline fixed at 19:00
    task['completed_work'] = 0  # Initialize completed work time (clearer naming)

# Ensure current time is within working hours
temp_date = get_next_working_time(current_date)
print(f"Adjusted start time: {temp_date.strftime('%Y-%m-%d %H:%M')}")

# Calculate available working hours before deadline (only counting hours during work time)
def calculate_available_working_hours(start_date, deadline):
    # Daily work hours
    daily_work_hours = WORK_END_HOUR - WORK_START_HOUR
    
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
        end_hour = min(DEADLINE_HOUR, WORK_END_HOUR)
        start_hour = max(current_date.hour, WORK_START_HOUR)
        # If start time is already past end time, no time available
        if start_hour >= end_hour:
            return 0
        hours_today = end_hour - start_hour
        total_hours += hours_today
        return total_hours
    else:
        # If not deadline day, can use extended work time
        if current_date.hour < WORK_END_HOUR:
            # Calculate remaining work time today
            start_hour = max(current_date.hour, WORK_START_HOUR)
            hours_today = WORK_END_HOUR - start_hour
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
        hours_deadline_day = max(0, DEADLINE_HOUR - WORK_START_HOUR)
        total_hours += hours_deadline_day
    
    return total_hours

# Check if there's enough working time to complete all tasks
def check_time_sufficiency(tasks, current_date):
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
        available_hours = calculate_available_working_hours(current_date, current_deadline)
        
        # Calculate total work time needed (all tasks with deadlines before or equal to current deadline)
        required_hours = sum(float(task['duration']) - task.get('completed_work', 0) for task in accumulated_tasks)
        
        print(f"\nDeadline {current_deadline.strftime('%Y-%m-%d %H:%M')} check:")
        print(f"  Total work time needed: {required_hours:.2f} hours")
        print(f"  Available work time: {available_hours:.2f} hours")
        
        if required_hours > available_hours:
            insufficient_deadlines.append((current_deadline, required_hours, available_hours))
    
    return insufficient_deadlines

# Adjust work end time
def adjust_work_end_time(insufficient_deadlines, current_date):
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
            print(f"Warning: Already on deadline day {deadline.strftime('%Y-%m-%d')}, cannot extend work hours")
            continue
        
        # Additional hours needed per day
        additional_hours_per_day = math.ceil(shortage / working_days)
        max_additional_hours_needed = max(max_additional_hours_needed, additional_hours_per_day)
    
    # Ensure additional time is a multiple of 2 (convenient for 2-hour work sessions)
    if max_additional_hours_needed % 2 != 0:
        max_additional_hours_needed += 1
    
    # Ensure new end time doesn't exceed midnight
    new_end_hour = min(24, WORK_END_HOUR + max_additional_hours_needed)
    
    # If new end time is midnight but still not enough, give warning
    if new_end_hour == 24 and max_additional_hours_needed > (24 - WORK_END_HOUR):
        print(f"Warning: Even working until midnight, still short {max_additional_hours_needed - (24 - WORK_END_HOUR)} hours per day")
        print("Suggestion: Consider extending project deadlines or reducing task workload")
    
    return new_end_hour

# Update working hours and recalculate all tasks' times
def update_working_hours(new_end_hour):
    global WORK_END_HOUR
    WORK_END_HOUR = new_end_hour
    print(f"Working hours adjusted to {WORK_START_HOUR}:00-{WORK_END_HOUR}:00")

# Periodically check if work time adjustment is needed in main loop
def check_and_adjust_working_hours(tasks, current_date):
    # Filter future tasks (deadlines after current date and not completed)
    future_tasks = [task for task in tasks if task['deadline'] > current_date and float(task['duration']) - task.get('completed_work', 0) > 0]
    
    if not future_tasks:
        # If no future tasks, restore standard working hours
        print("\nAll future tasks completed, restoring standard working hours (9:00-19:00)")
        update_working_hours(19)
        return
    
    # Save current work end time to check if standard work time is enough
    current_work_end_hour = WORK_END_HOUR
    
    # Temporarily set work time to standard (19:00) for calculation
    temp_work_end_hour = 19
    update_working_hours(temp_work_end_hour)
    
    # Check if standard work time is enough for all future tasks
    insufficient_deadlines = check_time_sufficiency(future_tasks, current_date)
    
    if not insufficient_deadlines:
        # If standard work time is enough, keep 19:00 end
        print("\nRemaining time is sufficient to complete all future tasks within standard work hours (9:00-19:00)")
        return
    else:
        # If standard work time is not enough, calculate how much extension is needed
        print("\nStandard work hours (9:00-19:00) are not sufficient to complete all future tasks, need to extend work hours")
        # Restore previous work end time for recalculation
        update_working_hours(current_work_end_hour)
        
        # Recalculate if time adjustment is needed under current conditions
        insufficient_deadlines = check_time_sufficiency(future_tasks, current_date)
        
        if not insufficient_deadlines:
            # If current time is enough (may have been extended), keep it
            print(f"\nCurrent work hours (9:00-{WORK_END_HOUR}:00) are sufficient to complete all future tasks")
            return
        
        # Calculate needed new end time
        new_end_hour = adjust_work_end_time(insufficient_deadlines, current_date)
        
        # Ensure new end time is not earlier than current end time (unless can return to 19:00)
        if 19 < new_end_hour < current_work_end_hour:
            new_end_hour = current_work_end_hour
            print(f"\nMaintaining current work hours {WORK_START_HOUR}:00-{current_work_end_hour}:00")
            return
        
        # Update work hours
        update_working_hours(new_end_hour)
        print(f"\nAdjusted work hours to {WORK_START_HOUR}:00-{WORK_END_HOUR}:00 to ensure completion of all future tasks")

def recalculate_all_tasks(tasks, current_date):
    """Recalculate available time and urgency for all tasks"""
    for task in tasks:
        if current_date < task['deadline']:
            # Calculate effective work time before deadline (only considering hours during work time)
            time_to_deadline = calculate_available_working_hours(current_date, task['deadline'])
            task['time_to_deadline'] = time_to_deadline
            
            # Update urgency
            duration = float(task['duration'])
            duration_left = max(0, duration - task.get('completed_work', 0))
            
            if time_to_deadline <= 0:
                urgency = 100  # Past deadline
            elif duration_left <= 0:
                urgency = 0    # Task completed
            else:
                urgency = 100 * (duration_left / time_to_deadline)
            
            task['urgency'] = urgency  # Keep as float for more precise sorting
            task['duration_left'] = duration_left

# Let the daily check at 9:00 AM handle the initial work schedule check
print("\nProgram starting, work schedule will be checked at the first 9:00 AM...")

# Process all tasks by time point
continue_simulation = True
first_iteration = True
while continue_simulation:
    # Check if during working hours
    if is_working_hours(temp_date):
        print(f"\nCurrent time point: {temp_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Check if it's 9:00 AM of a new day (adjust work hours at 9:00 AM every day)
        # Moved here, before processing tasks
        if temp_date.hour == 9 and temp_date.minute == 0:
            print("\nNew day begins, checking today's work hour arrangement...")
            
            # Filter future tasks (deadlines after current date and not completed)
            future_tasks = [task for task in tasks if task['deadline'] > temp_date and float(task['duration']) - task.get('completed_work', 0) > 0]
            
            if not future_tasks:
                print("No tasks to complete, using standard work hours (9:00-19:00)")
                update_working_hours(19)
            else:
                # Save current work end time
                current_end_hour = WORK_END_HOUR
                
                # Temporarily set to standard work hours (9:00-19:00)
                update_working_hours(19)
                print("Checking if all tasks can be completed within standard work hours (9:00-19:00)...")
                
                # Check if standard work hours are sufficient
                insufficient_deadlines = check_time_sufficiency(future_tasks, temp_date)
                
                if not insufficient_deadlines:
                    print("Starting today, can restore standard work hours (9:00-19:00), task progress is good")
                    # Already set to 19:00, no need to change
                else:
                    print("Standard work hours are not sufficient to complete all tasks, need to extend work hours")
                    # Calculate needed new end time
                    new_end_hour = adjust_work_end_time(insufficient_deadlines, temp_date)
                    update_working_hours(new_end_hour)
                    print(f"Work hours adjusted to {WORK_START_HOUR}:00-{WORK_END_HOUR}:00")
            
            # Recalculate all tasks' time (because work hours may have changed)
            recalculate_all_tasks(tasks, temp_date)
        
        # Update status and urgency of all uncompleted tasks
        active_tasks = []
        for i, task in enumerate(tasks):
            # If current time is before deadline, update task
            if temp_date < task['deadline']:
                # Calculate urgency
                duration = float(task['duration'])
                # Calculate effective work time before deadline (only considering hours during work time)
                time_to_deadline = calculate_available_working_hours(temp_date, task['deadline'])
                duration_left = max(0, duration - task.get('completed_work', 0))  # Remaining work time
                
                # Calculate urgency: remaining work time / remaining available time
                if time_to_deadline <= 0:
                    urgency = 100  # Past deadline
                elif duration_left <= 0:
                    urgency = 0    # Task completed
                else:
                    urgency = 100 * (duration_left / time_to_deadline)
                
                task['urgency'] = urgency
                task['duration_left'] = duration_left
                task['time_to_deadline'] = time_to_deadline  # Store effective work time before deadline
                
                if duration_left > 0:  # Only consider uncompleted tasks
                    active_tasks.append((i, task))
        
        # If no active tasks, end simulation
        if not active_tasks:
            print("All tasks completed or deadline reached, ending simulation.")
            break
            
        # Sort tasks by urgency
        active_tasks.sort(key=lambda x: x[1]['urgency'], reverse=True)
        
        # Display status of all tasks
        print("\nCurrent task status:")
        for i, task in active_tasks:
            print(f"Task {i+1}: {task.get('name', task.get('assignment_name', 'Unnamed Task'))}")
            print(f"  Accumulated work time: {task.get('completed_work', 0)} hours")
            print(f"  Remaining work time: {task['duration_left']} hours")
            print(f"  Effective work time before deadline: {task['time_to_deadline']:.2f} hours")
            print(f"  Urgency: {task['urgency']:.2f}%")
        
        # Save current status to JSON file
        save_tasks_snapshot(tasks, temp_date)
        
        # Process most urgent task
        most_urgent_idx, most_urgent_task = active_tasks[0]
        
        if first_iteration:
            # First iteration, display most urgent task to be processed, but 09:00-11:00 work already completed
            most_urgent_task['completed_work'] = most_urgent_task.get('completed_work', 0) + 2  # Add 2 hours completed work
            
            # Update status after processing
            duration = float(most_urgent_task['duration'])
            time_to_deadline = calculate_available_working_hours(temp_date, most_urgent_task['deadline'])
            duration_left = max(0, duration - most_urgent_task['completed_work'])
            most_urgent_task['duration_left'] = duration_left
            most_urgent_task['time_to_deadline'] = time_to_deadline
            
            print(f"\nWill begin processing most urgent task: {most_urgent_task.get('name', most_urgent_task.get('assignment_name', 'Unnamed Task'))}")
            print(f"  Urgency: {most_urgent_task['urgency']:.2f}%")
            print(f"\nCompleted 2 hours of work on this task from 09:00-11:00")
            print(f"  Accumulated work time: {most_urgent_task['completed_work']} hours")
            print(f"  Remaining work time: {duration_left} hours")
            print(f"  Effective work time before deadline: {time_to_deadline:.2f} hours")
            first_iteration = False
        else:
            # Normal processing of most urgent task (not first iteration)
            most_urgent_task['completed_work'] = most_urgent_task.get('completed_work', 0) + 2  # Add 2 hours completed work
            
            # Update status after processing
            duration = float(most_urgent_task['duration'])
            time_to_deadline = calculate_available_working_hours(temp_date, most_urgent_task['deadline'])
            duration_left = max(0, duration - most_urgent_task['completed_work'])
            most_urgent_task['duration_left'] = duration_left
            most_urgent_task['time_to_deadline'] = time_to_deadline
            
            print(f"\nCompleted 2 hours of work on most urgent task: {most_urgent_task.get('name', most_urgent_task.get('assignment_name', 'Unnamed Task'))}")
            print(f"  Accumulated work time: {most_urgent_task['completed_work']} hours")
            print(f"  Remaining work time: {duration_left} hours")
            print(f"  Effective work time before deadline: {time_to_deadline:.2f} hours")
        
        # Ask user whether to continue
        print(f"\nCurrent time: {temp_date.strftime('%Y-%m-%d %H:%M')}")
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
        old_date = temp_date
        temp_date += timedelta(hours=2)
        print(f"Time advances: {old_date.strftime('%H:%M')} -> {temp_date.strftime('%H:%M')}")
        
        # If outside working hours, adjust to next working time
        if not is_working_hours(temp_date):
            old_date = temp_date
            temp_date = get_next_working_time(temp_date)
            print(f"Outside working hours, adjusted to: {old_date.strftime('%Y-%m-%d %H:%M')} -> {temp_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Print separator
        print("\n" + "#" * 50)
    else:
        # Not during working hours, skip to next working time
        old_date = temp_date
        temp_date = get_next_working_time(temp_date)
        print(f"Not during working hours, adjusted to: {old_date.strftime('%Y-%m-%d %H:%M')} -> {temp_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Print separator
        print("\n" + "#" * 50)

# Display final results for all tasks
print("\nFinal results for all tasks:")
for i, task in enumerate(tasks):
    duration = float(task['duration'])
    completed_work = task.get('completed_work', 0)
    duration_left = task.get('duration_left', max(0, duration - completed_work))
    urgency = task.get('urgency', 0)
    
    print(f"\nTask {i+1}:")
    print(f"Task name: {task.get('name', task.get('assignment_name', 'Unnamed Task'))}")
    print(f"Duration: {duration} hours")
    print(f"Completed time: {completed_work} hours")
    print(f"Remaining work time: {duration_left} hours")
    print(f"Urgency: {urgency:.2f}%")
    print(f"Deadline: {task['deadline'].strftime('%Y-%m-%d %H:%M')}")

# Save final results to output.json
final_tasks = []
for task in tasks:
    task_copy = task.copy()
    # Convert datetime objects to strings
    if 'deadline' in task_copy:
        task_copy['deadline'] = task_copy['deadline'].strftime("%Y-%m-%d %H:%M")
    final_tasks.append(task_copy)

with open('output.json', 'w') as f:
    json.dump(final_tasks, f, indent=4)
print("\nAll tasks processed, final results saved to output.json")