import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from a .env file (if applicable)
load_dotenv()

# Set your OpenAI API key from the environment variable
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

def add_ranks_to_assignments(json_path):
    # Load assignments from JSON file
    with open(json_path, 'r') as f:
        assignments = json.load(f)
    
    # Sort assignments by weighted_score in descending order
    sorted_assignments = sorted(assignments, key=lambda x: x["weighted_score"], reverse=True)
    
    # Assign ranks (1 for highest weighted_score)
    for idx, assignment in enumerate(sorted_assignments, start=1):
        assignment["rank"] = idx
    
    # Write the updated list back to the JSON file
    with open(json_path, 'w') as f:
        json.dump(sorted_assignments, f, indent=4)

def filter_json(input_json, keys_to_keep):
    # Receive a json and filter out the usual information
    if isinstance(input_json, dict):
        return {k: v for k, v in input_json.items() if k in keys_to_keep}
    elif isinstance(input_json, list):
        return [filter_json(item, keys_to_keep) for item in input_json]
    else:
        return input_json



def explain_priority(json_file):

    # (1) Add ranking
    add_ranks_to_assignments(json_file)

    # (2) Filter the json 
    keys_to_keep = ["assignment_name", "importance", "urgency", "mood", "rank"]

    # Read the JSON data
    with open(json_file, 'r') as f:
        assignments = json.load(f)
    
    new_assignment = filter_json(assignments, keys_to_keep)

    print(f"NEW: {new_assignment}")
    
    # Construct the prompt
    prompt = f"""
    You are an expert academic advisor who understands JSON data and can explain priorities in a friendly manner.
    
    The JSON data below represents the top three priority assignments that have been ranked based on several factors:
    - "assignment_name": The name of the assignment.
    - "rank": The priority ranking (with 1 being the highest).
    - "importance": How important the assignment is, where a higher number means more important (for example, it might be worth more in grades).
    - "urgency": A computed value representing how urgent the assignment is (for example, how much time is left until the deadline relative to the effort required).
    - "mood": A value between 0 and 10 indicating the user's preference for the assignment, where 10 means the user is very enthusiastic and 0 means the user is very reluctant (with 5 being neutral).
    
    Here is the JSON data:
    {json.dumps(assignments, indent=4)}
    
    Based on this data, please provide a clear, friendly, and detailed explanation for the user. Explain why each of the top three assignments is prioritized, referring to their urgency, importance, and mood values. Your explanation should be conversational and include insights like:
    - If an assignment has a high urgency value, explain that it needs immediate attention.
    - If an assignment is very important (high importance) or matches the user’s mood, highlight why it might be a good idea to start with it.
    Please provide a brief and human-like explanation for the user that does not focus too much on the exact numbers, but rather on the overall message. For example, explain that one assignment might need to be tackled immediately because it's very urgent or close to its deadline, while another might be important but less pressing. The response should be friendly, casual, and clear.
    Provide your answer in plain text.

    
    """
    
    # Make the API call
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert academic advisor."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        temperature=0.7,
    )
    
    # Clean up the response (remove Markdown code fences if necessary)
    raw_content = response.choices[0].message.content.strip()
    if raw_content.startswith("```"):
        lines = raw_content.splitlines()
        filtered_lines = [line for line in lines if not line.startswith("```")]
        raw_content = "\n".join(filtered_lines).strip()
    
    return raw_content

if __name__ == "__main__":
    explanation_text = explain_priority("/Users/maxlyu/Documents/AI_Hackathon/suggestion/tasks_20250101_0900.json")
    print("Explanation:\n", explanation_text)
