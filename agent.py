import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import os
import streamlit as st

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 300
    }
)


def ask_gemini(prompt):
    try:
        response = model.generate_content(
            prompt,
            request_options={"timeout": 30}
        )
        return response.text

    except ResourceExhausted:
        return "⚠️ Gemini API quota exceeded. Try again later."

    except Exception as e:
        return f"Error: {str(e)}"


def generate_tasks(goal):

    prompt = f"""
Break this goal into 8 simple tasks.

Goal: {goal}

Rules:
- Only tasks
- One per line
- No numbering
- No explanation
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
        return ask_gemini(prompt)

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