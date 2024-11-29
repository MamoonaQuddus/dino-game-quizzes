import streamlit as st
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the T5 model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google-t5/t5-base")

# Function to generate a math quiz question
def generate_math_quiz(prompt, num_questions=5):
    quizzes = []
    for _ in range(num_questions):
        inputs = tokenizer(prompt, return_tensors="pt", max_length=50, truncation=True)
        outputs = model.generate(inputs["input_ids"], max_length=50, num_return_sequences=1, do_sample=True)
        question = tokenizer.decode(outputs[0], skip_special_tokens=True)
        quizzes.append({"question": question, "answer": None})  # Placeholder for answer
    return quizzes

# Generate quizzes for different operations
math_operations = ["addition", "subtraction", "multiplication", "division"]
all_quizzes = {}

for operation in math_operations:
    prompt = f"Generate a math quiz question about {operation}."
    all_quizzes[operation] = generate_math_quiz(prompt, num_questions=5)

# Save quizzes to a JSON file
with open("math_quizzes.json", "w") as file:
    json.dump(all_quizzes, file)

print("Math quizzes generated and saved to math_quizzes.json!")
