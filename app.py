import streamlit as st
import requests

# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "lives" not in st.session_state:
    st.session_state.lives = 3  # Start with 3 lives
if "questions" not in st.session_state:
    st.session_state.questions = []

# Groq API settings
API_URL = "https://api.groq.com/openai/v1/chat/completions"  # Confirm this is the correct endpoint
API_KEY = " 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"  # Replace with your valid Groq API key

def fetch_questions(topic="math", num_questions=3):
    """
    Fetch quiz questions dynamically from the Groq API using llama-3.1-70b-versatile.
    """
    try:
        # Create the chat-style prompt for generating questions
        prompt = f"Generate {num_questions} {topic} quiz questions. Each question should include the correct answer."
        
        # Construct the payload
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 1,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False,
            "stop": None
        }

        # Set the headers
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # Make the API request
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise error for HTTP issues

        # Parse the API response
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Extract questions and answers from the response content
        questions = []
        for line in content.split("\n"):
            if line.strip().startswith("Question:"):
                question = line.replace("Question:", "").strip()
            elif line.strip().startswith("Answer:"):
                answer = line.replace("Answer:", "").strip()
                questions.append({"question": question, "answer": answer})  # Add question-answer pair

        return questions
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching questions: {e}")
        return []

# Function to reset the quiz
def reset_quiz():
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.lives = 3
    st.session_state.questions = []

# Fetch questions if not already fetched
if not st.session_state.questions:
    st.session_state.questions = fetch_questions("math", num_questions=3)

# Main quiz logic
st.title("Dino Game - Quiz Mode")
st.write("Answer the questions to regain lives!")

if st.session_state.lives > 0:  # Check if the player has lives left
    if st.session_state.current_question < len(st.session_state.questions):
        current_quiz = st.session_state.questions[st.session_state.current_question]
        st.write(f"**Question:** {current_quiz['question']}")
        user_answer = st.text_input("Your Answer", key=f"q{st.session_state.current_question}")

        if st.button("Submit", key=f"submit_{st.session_state.current_question}"):
            if user_answer:
                if user_answer.lower() == current_quiz["answer"].lower():  # Compare with the correct answer
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
