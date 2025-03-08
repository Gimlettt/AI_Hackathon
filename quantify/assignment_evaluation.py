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

def create_assignments_json(pdf_paths):
    assignments = []

    for i in range(len(pdf_paths)):
        print(f"\nAssignment {i+1}")
        name = pdf_paths[i]
        ddl = f"3/{random.randrange(11,24)}"
        importance = random.randrange(0,10)
        user_comment = input("Enter your comment: ")

        content = extract_text_from_pdf(pdf_paths[i])

        assignment = {
            "assignment_name": name,
            "DDL": ddl,
            "content": content,
            "importance": importance,
            "user_comment": user_comment
        }

        assignments.append(assignment)

    with open('raw.json', 'w') as f:
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



def process_assignments(input_file, output_file):
    with open(input_file, 'r') as f:
        assignments = json.load(f)

    results = []

    for assignment in assignments:
        print(f"Evaluating assignment: {assignment['assignment_name']}...")
        difficulty_result = evaluate_difficulty(assignment['content'])
        duration_result = evaluate_duration(assignment['content'])

        results.append({
            "assignment_name": assignment["assignment_name"],
            "DDL": assignment["DDL"],
            "importance": assignment["importance"],
            "difficulty": difficulty_result["difficulty"],
            "difficulty_explanation": difficulty_result["explanation"],
            "estimated_duration_hours": duration_result["duration_hours"],
            "duration_explanation": duration_result["explanation"]
        })

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Evaluation complete. Results saved to {output_file}")


if __name__ == "__main__":

    # assignments = []
    # pdfs = ["handouts/3F7 EP2.pdf", "handouts/3F8_FTR_edited.pdf", "handouts/CUES CUCaTS AI Agent Hackathon Rulebook.pdf", "handouts/examp3.pdf"]
    # create_assignments_json(pdfs)

    process_assignments("raw.json", "output.json")
