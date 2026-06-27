import streamlit as st
import json


from agent import generate_tasks
from agent import analyze_progress
from agent import prioritize_tasks
from agent import create_daily_plan
from agent import chat_with_agent
from agent import generate_quiz
from datetime import date
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_certificate_pdf(course_name):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "CERTIFICATE OF COMPLETION",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "This certifies that the learner has successfully completed:",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"<b>{course_name}</b>",
            styles["Heading2"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"Completion Date: {date.today()}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Congratulations on your achievement!",
            styles["Normal"]
        )
    )

    doc.build(content)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf




st.title("AI To-Do Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "quiz_task" not in st.session_state:
    st.session_state.quiz_task = None

if "show_quiz" not in st.session_state:
    st.session_state.show_quiz = False

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "show_certificate" not in st.session_state:
    st.session_state.show_certificate = False

if "course_name" not in st.session_state:
    st.session_state.course_name = ""

# ------------------------------
# AI Assistant Chat
# ------------------------------

if st.button("💬"):
    st.session_state.show_chat = (
        not st.session_state.show_chat
    )

if st.session_state.show_chat:

    with st.sidebar:

        st.subheader("💬 AI Assistant")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input(
            "Ask about your tasks, progress, goals..."
        )

        if prompt:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with open("tasks.json", "r") as file:
                tasks = json.load(file)

            response = chat_with_agent(
                prompt,
                tasks
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

# ------------------------------
# Quiz Sidebar
# ------------------------------
if st.session_state.show_quiz:

    with st.sidebar:

        st.subheader(
            f"📝 {st.session_state.quiz_task}"
        )

        try:

            quiz_text = st.session_state.quiz_data

            quiz_text = quiz_text.replace(
                "```json", ""
            )

            quiz_text = quiz_text.replace(
                "```", ""
            )

            quiz_questions = json.loads(
                quiz_text.strip()
            )

            answers = []

            for i, q in enumerate(quiz_questions):

                answer = st.radio(
                    q["question"],
                    q["options"],
                    key=f"quiz_{i}"
                )

                answers.append(answer)

                # Show result below each question
                if st.session_state.quiz_submitted:

                    if (
                        answer.strip().lower()
                        ==
                        q["answer"].strip().lower()
                    ):

                        st.success("✅ Correct")

                    else:

                        st.error(
                            f"❌ Correct Answer: {q['answer']}"
                        )

            if st.button("Submit Quiz"):

                score = 0

                for i, q in enumerate(
                    quiz_questions
                ):

                    if (
                        answers[i].strip().lower()
                        ==
                        q["answer"].strip().lower()
                    ):

                        score += 1

                st.session_state.quiz_score = score
                st.session_state.quiz_submitted = True

                st.rerun()

            if st.session_state.quiz_submitted:

                score = st.session_state.quiz_score

                st.success(
                    f"🎯 Score: {score}/{len(quiz_questions)}"
                )

                if score >= 7:

                    st.balloons()
                    st.success(
                        "✅ Quiz Passed"
                    )

                else:

                    st.error(
                        "❌ Quiz Failed"
                    )

            if st.button("Close Quiz"):

                st.session_state.show_quiz = False
                st.session_state.quiz_data = None
                st.session_state.quiz_task = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score = 0

                st.rerun()

        except Exception as e:

            st.error(
                "Quiz loading failed."
            )

            st.write(e)
# ------------------------------
# Generate Tasks From Goal
# ------------------------------

with open("tasks.json", "r") as file:
    tasks = json.load(file)

total_tasks = len(tasks)

completed_tasks = sum(
    1 for task in tasks
    if task["status"] == "Completed"
)


pending_tasks = total_tasks - completed_tasks

all_tasks_completed = (
    total_tasks > 0
    and completed_tasks == total_tasks
)

completion_rate = 0

if total_tasks > 0:
    completion_rate = (
        completed_tasks / total_tasks
    ) * 100

st.subheader("📊 Progress Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", total_tasks)
col2.metric("Completed", completed_tasks)
col3.metric("Pending", pending_tasks)
col4.metric("Completion %", f"{completion_rate:.1f}%")



st.subheader("Generate Tasks From Goal")

goal = st.text_area("Enter Your Goal")

# Buttons in same row
btn1, btn2 = st.columns([4, 1])

with btn1:
    generate_clicked = st.button("Generate Tasks")

with btn2:
    reset_clicked = st.button("Reset All Tasks")

# Generate Tasks
if generate_clicked:
    st.session_state.course_name = goal

    ai_tasks = generate_tasks(goal)

    with open("tasks.json", "r") as file:
        tasks = json.load(file)

    for task in ai_tasks.split("\n"):

        task = task.strip()

        if task:

            tasks.append({
                "task": task,
                "status": "Pending"
            })

    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)

    st.success("Tasks Generated Successfully!")
    st.rerun()

# Reset Tasks
if reset_clicked:

    with open("tasks.json", "w") as file:
        json.dump([], file, indent=4)

    st.success("All tasks deleted!")
    st.rerun()

# ------------------------------
# Display Tasks
# ------------------------------


st.subheader("My Tasks")

with open("tasks.json", "r") as file:
    tasks = json.load(file)

for index, item in enumerate(tasks):

    col1, col2, col3, col4 = st.columns([5, 2, 2, 2])

    with col1:
        st.write(
            f"{item['task']} - {item['status']}"
        )

    with col2:

        if st.button(
            "Complete",
            key=f"c{index}"
        ):

            tasks[index]["status"] = "Completed"

            with open("tasks.json", "w") as file:
                json.dump(
                    tasks,
                    file,
                    indent=4
                )

            st.rerun()

    with col3:

        if st.button(
            "Delete",
            key=f"d{index}"
        ):

            tasks.pop(index)

            with open("tasks.json", "w") as file:
                json.dump(
                    tasks,
                    file,
                    indent=4
                )

            st.rerun()


    with col4:

      if st.button(
        "Quiz",
        key=f"q{index}"
    ):

        quiz = generate_quiz(
            item["task"]
        )

        st.session_state.quiz_data = quiz
        st.session_state.quiz_task = item["task"]
        st.session_state.show_quiz = True
        st.session_state.quiz_submitted = False
        st.session_state.quiz_score = 0 

        st.rerun()


# ------------------------------
# Generate Certificate Button
# ------------------------------

if all_tasks_completed:

    st.success(
        "🎉 Congratulations! You completed all tasks."
    )

    if st.button(
        "🏆 Generate Certificate",
        key="generate_certificate"
    ):

        st.session_state.show_certificate = True
        st.rerun()


# ------------------------------
# Certificate
# ------------------------------

if st.session_state.show_certificate:

    st.markdown("---")

    st.markdown(
        f"""
# 🏆 Certificate of Completion

Successfully completed:

## {st.session_state.course_name}

📅 Completion Date: {date.today()}
"""
    )

    pdf_data = create_certificate_pdf(
        st.session_state.course_name
    )

    st.download_button(
        label="📄 Download PDF Certificate",
        data=pdf_data,
        file_name="certificate.pdf",
        mime="application/pdf"
    )