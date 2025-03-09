import json
import os

# Merges the mood values into the subjective value
# subjective_json is the ddl driven, difficulty driven param
# objective_json is the json containing mood
def merge_mood_json(subjective_json_list):
  # Get the absolute path of the current script (inside ./audio)
  current_dir = os.path.dirname(os.path.abspath(__file__))
  # Construct the path to the JSON file
  json_path = os.path.join(current_dir, "..", "audio", "output.json")
  # Read the JSON file
  with open(json_path, "r", encoding="utf-8") as file:
    objective_json_list = json.load(file)
  
  if isinstance(objective_json_list, list):  # Check if it's already a list
    print("[merging] returned_json is already a Python list.")
  elif isinstance(objective_json_list, dict):  # Check if it's a single dictionary
    print("[merging] returned_json is a dictionary. Wrapping in a list.")
    objective_json_list = [objective_json_list]  # Wrap in a list for consistency
    
  print(objective_json_list)
  # Updating mood values in list_two based on list_one
  for mood_json in objective_json_list:
    print(mood_json)
    event_name = mood_json["event_name"]
    mood_value = mood_json["mood"]
    
    for subjective_json in subjective_json_list:
      if subjective_json["module"] == event_name:
        print(f"mood for {subjective_json['module']} was {subjective_json['mood']}")
        subjective_json["mood"] = mood_value  # Update mood
        print(f"mood for {subjective_json['module']} is now {subjective_json['mood']}")
  
  # Return updated subjective json list
  return subjective_json_list

  
  

if __name__ == "__main__":
  # Get the absolute path of the current script (inside ./audio)
  current_dir = os.path.dirname(os.path.abspath(__file__))
  # Construct the path to the JSON file
  json_path = os.path.join(current_dir, "eval_example.json")
  # Read the JSON file
  with open(json_path, "r", encoding="utf-8") as file:
    subjective_json = json.load(file)
  
  print(merge_mood_json(subjective_json))
