import os
from openai import OpenAI
from dotenv import load_dotenv  # Only needed if you use a .env file
from PyPDF2 import PdfReader
import json
import random


# Load environment variables from a .env file (if applicable)
load_dotenv()

# # Set your OpenAI API key from the environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)


def extract_text_from_pdf(pdf_path):

    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text.strip()

def create_assignments_json(folder_path):
    assignments = []
    # List all files in the folder and filter for PDFs
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

    for i, pdf_file in enumerate(pdf_files):
        name = os.path.splitext(os.path.basename(pdf_file))[0]
        print(f"\nAssignment {i+1}: {name}")
        ddl = f"1/{random.randrange(2, 15)}"
        user_comment = input("Enter your comment: ")

        # Create full file path
        pdf_path = os.path.join(folder_path, pdf_file)
        content = extract_text_from_pdf(pdf_path)

        assignment = {
            "assignment_name": name,
            "DDL": ddl,
            "content": content,
            "user_comment": user_comment
        }
        assignments.append(assignment)

    json_file = os.path.join(os.path.dirname(__file__), "raw.json")
    with open(json_file, 'w') as f:
        json.dump(assignments, f, indent=4)

def evaluate_difficulty(content):
    prompt = f"""
    Based on the assignment content provided below, evaluate how difficult this assignment is.
    Provide a difficulty score between 0 (easiest) and 10 (hardest) with a brief explanation (1-2 sentences).

    Assignment content:
    \"\"\"
    {content}
    \"\"\"

    Respond in the following JSON format:
    {{
        "difficulty": <difficulty_score>,
        "explanation": "<explanation_here>"
    }}
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert evaluator."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
        temperature=0.3,
    )
    raw_content = response.choices[0].message.content.strip()
    # Remove Markdown code fences if present
    if raw_content.startswith("```"):
        lines = raw_content.splitlines()
        filtered_lines = [line for line in lines if not line.startswith("```")]
        raw_content = "\n".join(filtered_lines).strip()
    response_json = json.loads(raw_content)
    return response_json

def evaluate_importance(content, user_comment, type):
    prompt = f"""
    Based on the assignment content and user's comment, evaluate how important this assignment is. User comment might express student's opinion about the importance of assignment.
    In addition, the assignment's importance is related to its type. If the assignment is a CW (coursework), it counters toward final grade and should be treated with more attention.
    If the assignment is a EP (example paper), it is a ungraded worksheet that doesn't affect final grade. 

    Provide a difficulty score between 0 (least important) and 10 (most important) with a brief explanation (1 sentence).

    Assignment content:
    \"\"\"
    {content}
    \"\"\"

    The assignment is of {type} type. 
    Respond in the following JSON format:
    {{
        "importance": <difficulty_score>,
        "explanation": "<explanation_here>"
    }}
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert evaluator."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
        temperature=0.3,
    )
    raw_content = response.choices[0].message.content.strip()
    # Remove Markdown code fences if present
    if raw_content.startswith("```"):
        lines = raw_content.splitlines()
        filtered_lines = [line for line in lines if not line.startswith("```")]
        raw_content = "\n".join(filtered_lines).strip()
    response_json = json.loads(raw_content)
    return response_json


def evaluate_duration(content):
    prompt = f"""
    Based on the assignment content provided below, estimate how long it would take a student to complete this assignment.
    Provide an estimated duration in hours (this can be a decimal value) along with a brief explanation (1-2 sentences).

    Assignment content:
    \"\"\"
    {content}
    \"\"\"

    Respond in the following JSON format:
    {{
        "duration_hours": <estimated_duration>,
        "explanation": "<explanation_here>"
    }}
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert evaluator."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
        temperature=0.3,
    )
    raw_content = response.choices[0].message.content.strip()
    if raw_content.startswith("```"):
        lines = raw_content.splitlines()
        filtered_lines = [line for line in lines if not line.startswith("```")]
        raw_content = "\n".join(filtered_lines).strip()
    response_json = json.loads(raw_content)
    return response_json

def classify_assignment_type(content):
    prompt = f"""
    Based on the assignment content provided below, determine whether the assignment is a (1)coursework (2)example paper, worksheet.
    The answer should be either CW for coursework, or EP for example paper. Nothing else. 
    Assignment content:
    \"\"\"
    {content}
    \"\"\"

    Respond in the following JSON format:
    {{
        "type": <answer>,
    }}

    Again, the answer should only be either "CW" or "EP"
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert evaluator."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
        temperature=0.3,
    )
    raw_content = response.choices[0].message.content.strip()
    if raw_content.startswith("```"):
        lines = raw_content.splitlines()
        filtered_lines = [line for line in lines if not line.startswith("```")]
        raw_content = "\n".join(filtered_lines).strip()
    response_json = json.loads(raw_content)
    return response_json

def process_assignments(input_file, output_file):
    with open(input_file, 'r') as f:
        assignments = json.load(f)

    results = []

    for assignment in assignments:
        print(f"Evaluating assignment: {assignment['assignment_name']}...")
        difficulty_result = evaluate_difficulty(assignment['content'])
        duration_result = evaluate_duration(assignment['content'])
        assignment_type = classify_assignment_type(assignment['content'])
        importance_result = evaluate_importance(assignment['content'], assignment["user_comment"], assignment_type["type"])
        module = classify_assignment_module(course_dict_json=course_description_json, assignment_content=assignment['content'])

        results.append({
            "assignment_name": assignment["assignment_name"],
            "DDL": assignment["DDL"],
            "importance": importance_result["importance"],
            "difficulty": difficulty_result["difficulty"],
            "difficulty_explanation": difficulty_result["explanation"],
            "duration": duration_result["duration_hours"],
            "duration_explanation": duration_result["explanation"],
            "module": module,
            "type": assignment_type["type"]
        })

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Evaluation complete. Results saved to {output_file}")

def classify_assignment_module(course_dict_json, assignment_content):

    with open(course_dict_json, 'r') as f:
        course_dict = json.load(f)
        keys_str = ", ".join(course_dict.keys())

    prompt = f"""
    You are an academic advisor. Given the following dictionary of courses and their descriptions:
    {json.dumps(course_dict_json, indent=4)}
    
    Classify the following assignment content into one of the courses. Respond with exactly one of the following course codes (and nothing else): {keys_str}. Please follow this rule strictly.
    
    Assignment content:
    \"\"\"
    {assignment_content}
    \"\"\"
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert academic advisor."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()



def manual_new_assignment(pdf_path, raw_json_path, eval_json_path):
    ## (1) Update the raw.json
    if os.path.exists(raw_json_path):
        with open(raw_json_path, 'r') as f:
            try:
                assignments = json.load(f)
            except json.JSONDecodeError:
                assignments = []
    else:
        assignments = []
    
    print(f"Adding new assignment from PDF: {pdf_path}")

    name = pdf_path
    ddl = f"1/{random.randrange(2,15)}"
    content = extract_text_from_pdf(pdf_path)
    importance = random.randrange(0,10)
    user_comment = input("How do you feel about the assignment?")

    new_assignment = {
        "assignment_name": name,
        "DDL": ddl,
        "content": content,
        "importance": importance,
        "user_comment": user_comment
    }

    assignments.append(new_assignment)
    
    # Write the updated list back to the JSON file
    with open(raw_json_path, 'w') as f:
        json.dump(assignments, f, indent=4)


    ## (2) Update the eval.json (including the evaluation results from LLM)
    if os.path.exists(eval_json_path):
        with open(eval_json_path, 'r') as f:
            try:
                eval_result = json.load(f)
            except json.JSONDecodeError:
                eval_result = []
    else:
        eval_result = []
    

    print(f"Evaluating assignment: {name}...")
    difficulty_result = evaluate_difficulty(content)
    duration_result = evaluate_duration(content)
    assignment_type = classify_assignment_type(content)
    module = classify_assignment_module(course_dict_json=course_description_json, assignment_content=content)


    eval_result.append({
        "assignment_name": name,
        "DDL": ddl,
        "importance": importance,
        "difficulty": difficulty_result["difficulty"],
        "difficulty_explanation": difficulty_result["explanation"],
        "estimated_duration_hours": duration_result["duration_hours"],
        "duration_explanation": duration_result["explanation"],
        "module": module,
        "type": assignment_type["type"]
    })
    
    # Write the updated list back to the JSON file
    with open(eval_json_path, 'w') as f:
        json.dump(eval_result, f, indent=4)


def read_pdf():
    pdf_folder = os.path.join(os.path.dirname(__file__), "..", "handouts")
    create_assignments_json(pdf_folder)

def quantify_pdf():
    raw_json = os.path.join(os.path.dirname(__file__), "raw.json")
    eval_json = os.path.join(os.path.dirname(__file__), "eval.json")
    process_assignments(raw_json, eval_json)

if __name__ == "__main__":

    # course_description_json = "/Users/maxlyu/Documents/AI_Hackathon/quantify/course_description.json"
    course_description_json = os.path.join(os.path.dirname(__file__), "course_description.json")

    read_pdf()
    quantify_pdf()

    # pdf_folder = "/Users/maxlyu/Documents/AI_Hackathon/handouts"
    # create_assignments_json(pdf_folder)

    # raw_json = os.path.join(os.path.dirname(__file__), "raw.json")
    # eval_json = os.path.join(os.path.dirname(__file__), "eval.json")
    # process_assignments(raw_json, eval_json)

    # manual_new_assignment("/Users/maxlyu/Documents/AI_Hackathon/quantify/4F13_cw1.pdf","/Users/maxlyu/Documents/AI_Hackathon/raw.json","/Users/maxlyu/Documents/AI_Hackathon/output.json")
