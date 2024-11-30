import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv('GROQ_API_KEY')

# Initialize ChatGroq
llm = ChatGroq(
    api_key=api_key,
    model="llama-3.1-70b-versatile",  # Specify your desired model
    temperature=1.0,                  # Set temperature for creative output
    max_retries=2                     # Set maximum retries for requests
)

# Function to generate quiz questions
def generate_questions(topic="math", num_questions=3):
    """
    Generate quiz questions without answers.
    """
    try:
        prompt = f"Generate {num_questions} {topic} multiple-choice quiz questions with 4 options each. Do not include answers."
        response = llm.invoke([  
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])
        content = response.content if hasattr(response, 'content') else str(response)

        # Debug: Print raw content
        print("Raw Questions Content:", content)

        # Parse questions
        questions = []
        current_question = {"options": []}

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
                # Save the previous question if present
                if current_question and "question" in current_question:
                    questions.append(current_question)
                    current_question = {"options": []}

                current_question["question"] = line

            elif line.startswith("A)") or line.startswith("B)") or line.startswith("C)") or line.startswith("D)"):
                # Append options
                current_question["options"].append(line)

        # Add the last question if it exists
        if current_question and "question" in current_question:
            questions.append(current_question)

        return questions if questions else []
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

# Function to fetch concise answers (A, B, C, D) for the provided questions
def fetch_answers(questions):
    """
    Fetch concise answers (A, B, C, or D) for the provided questions.
    """
    try:
        prompt = "Provide the correct answers for the following multiple-choice questions in concise form (e.g., A, B, C, or D). Only return the letter of the correct answer for each question:\n"
        for i, question in enumerate(questions):
            prompt += f"\n{i + 1}. {question['question']}\n"
            for option in question["options"]:
                prompt += f"{option}\n"

        response = llm.invoke([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])
        content = response.content if hasattr(response, 'content') else str(response)

        # Debug: Print raw answers content
        print("Raw Answers Content:", content)

        # Extract concise answers (e.g., A, B, C, or D)
        answers = {}
        for line in content.split("\n"):
            line = line.strip()
            if line and len(line) == 1 and line.upper() in ["A", "B", "C", "D"]:
                question_number = len(answers)  # Match order with the question index
                answers[question_number] = line.upper()

        return answers
    except Exception as e:
        st.error(f"Error fetching answers: {e}")
        return {}

# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "lives" not in st.session_state:
    st.session_state.lives = 3
if "questions" not in st.session_state or not st.session_state.questions:
    st.session_state.questions = generate_questions("math", num_questions=3)
if "answers" not in st.session_state or not st.session_state.answers:
    st.session_state.answers = fetch_answers(st.session_state.questions)

# Function to reset the quiz
def reset_quiz():
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.lives = 3
    st.session_state.questions = generate_questions("math", num_questions=3)
    st.session_state.answers = fetch_answers(st.session_state.questions)

# Main quiz logic
st.title("Dino Game - Quiz Mode")
st.write("Answer the questions to regain lives!")

if st.session_state.lives > 0:  # Check if the player has lives left
    if st.session_state.current_question < len(st.session_state.questions):
        current_quiz = st.session_state.questions[st.session_state.current_question]
        correct_answer = st.session_state.answers.get(st.session_state.current_question, "").lower()

        # Display the question and options
        st.write(f"**Question:** {current_quiz['question']}")
        for option in current_quiz["options"]:
            st.write(option)

        # Input for user answer
        user_answer = st.text_input("Your Answer (e.g., A, B, C, or D)", key=f"q{st.session_state.current_question}")

        if st.button("Submit", key=f"submit_{st.session_state.current_question}"):
            if user_answer:
                print("correct answer", correct_answer)
                print("user answer", user_answer.lower())
                if user_answer.lower() == correct_answer:  # Compare with the correct answer
                    st.success("Correct!")
                    st.session_state.score += 1
                    st.session_state.current_question += 1
                    st.session_state.attempts = 0
                else:
                    st.error("Wrong! Try again.")
                    st.session_state.attempts += 1
                    if st.session_state.attempts >= 3:  # Max retries reached
                        st.warning("Maximum attempts reached! Moving to the next question.")
                        st.session_state.lives -= 1  # Decrease life if wrong attempts exceed limit
                        st.session_state.current_question += 1
                        st.session_state.attempts = 0
            else:
                st.warning("Please enter an answer before submitting.")
    else:
        st.write(f"Quiz completed! **Score:** {st.session_state.score}/{len(st.session_state.questions)}")
        if st.session_state.score == len(st.session_state.questions):
            st.write("You answered all questions correctly! Restoring lives.")
            st.session_state.lives = 3  # Restore lives if all questions were answered correctly
        if st.button("Restart Quiz"):
            reset_quiz()
else:
    st.write("You have no lives left! Returning to the main game.")
    if st.button("Exit Quiz Mode"):
        # Reset quiz and return to main game
        reset_quiz()
