import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text

    except ResourceExhausted:
        return (
            "⚠️ Gemini API quota exceeded. "
            "Please wait for the quota reset or use another API key."
        )

    except Exception as e:
        return f"Error: {str(e)}"


def generate_tasks(goal):

    prompt = f"""
    Convert the following goal into a practical task list.

    Goal:
    {goal}

    Return only task names.
    One task per line.
    """

    return ask_gemini(prompt)


def analyze_progress(tasks):

    prompt = f"""
    You are an AI career coach.

    Analyze the user's completed and pending tasks.

    Tell:
    1. What progress has been made.
    2. What skills are already covered.
    3. What should be focused on next.
    4. One motivational suggestion.

    Tasks:
    {tasks}
    """

    return ask_gemini(prompt)


def prioritize_tasks(tasks):

    prompt = f"""
    Categorize the following tasks into:

    High Priority
    Medium Priority
    Low Priority

    Tasks:
    {tasks}

    Return in a clean format.
    """

    return ask_gemini(prompt)


def create_daily_plan(tasks, available_hours):

    prompt = f"""
    You are an AI productivity coach.

    Create a daily plan based on:

    Available Hours:
    {available_hours}

    Tasks:
    {tasks}

    Only consider pending tasks.

    Allocate time wisely.

    Return:
    - Ordered task list
    - Time allocation
    - Short explanation
    """

    return ask_gemini(prompt)


def chat_with_agent(user_query, tasks):

    prompt = f"""
    You are an AI Productivity Assistant.

    Current Task Data:
    {tasks}

    User Question:
    {user_query}

    Answer using the task data whenever possible.
    """

    return ask_gemini(prompt)


def generate_quiz(task):

    prompt = f"""
    Create exactly 10 multiple choice questions about:

    {task}

    Return ONLY a JSON array.

    Do NOT use markdown.
    Do NOT use ```json.
    Do NOT add explanations.

    Format:

    [
      {{
        "question": "...",
        "options": ["A","B","C","D"],
        "answer": "..."
      }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except ResourceExhausted:
        return """
[
    {
        "question": "Gemini API quota exceeded. Please try again later.",
        "options": ["OK"],
        "answer": "OK"
    }
]
"""

    except Exception as e:
        return f"""
[
    {{
        "question": "Error: {str(e)}",
        "options": ["OK"],
        "answer": "OK"
    }}
]
"""