import streamlit as st
import json

# Load math quiz data
with open("math_quizzes.json", "r") as file:
    quizzes = json.load(file)

# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "current_operation" not in st.session_state:
    st.session_state.current_operation = "addition"

# Sidebar for selecting math operation
st.sidebar.title("Math Quiz Settings")
st.session_state.current_operation = st.sidebar.selectbox(
    "Choose a Math Operation:",
    options=quizzes.keys()
)

# Get questions for the selected operation
operation_questions = quizzes[st.session_state.current_operation]

# Display the quiz
st.title("Math Quiz")
if st.session_state.current_question < len(operation_questions):
    current_quiz = operation_questions[st.session_state.current_question]
    st.write(f"**Question:** {current_quiz['question']}")

    user_answer = st.text_input("Your Answer", key="answer")
    if st.button("Submit"):
        # For now, assume the answer is always correct
        st.success("Correct!")
        st.session_state.score += 1
        st.session_state.current_question += 1
else:
    st.write("You've completed all questions!")
    st.write(f"**Your Score:** {st.session_state.score}/{len(operation_questions)}")

if st.button("Reset Quiz"):
    st.session_state.current_question = 0
    st.session_state.score = 0

