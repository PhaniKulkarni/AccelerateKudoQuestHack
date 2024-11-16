""" This module contains the Quiz AI Agent that generates questions based on a given topic. """

"""Step 1: Import necessary modules"""
from services.azure_open_ai import get_azure_openai_llm

"""Step 2: Define the function to generate questions"""
def generate_questions(topic, num_questions=5):
    """
    Generates questions based on a given topic.

    Args:
        topic (str): The topic for which to generate questions.
        num_questions (int): The number of questions to generate.

    Returns:
        dict: A dictionary containing questions, options for MCQs, and correct answers.
    """
    questions = {}
    llm = get_azure_openai_llm()  # Get the Azure language model

    # Example prompt structure for generating questions
    prompt = (
        f"Generate {num_questions} questions about {topic} either along with four answer choices, or one short answer. "
        f"Split each question-answer pair on a separate line. "
        f"Split the question and the options each by the text [&&]. "
        f"Also mention whether it's multiple choice (MC) or short answer (SA). "
        f"Ex: MC[&&]Question?[&&]Answer1[&&]Answer2[&&]Answer3[&&]Answer4, new line, then question 2. "
        f"For SA, ex: SA[%%]Question?[&&]Answer"
    )

    try:
        response = llm(prompt)  # Call the Azure LLM with the prompt
        generated_text = response.content.strip()  # Get the text response from the LLM

        # Process the generated text to extract questions
        for line in generated_text.splitlines():
            if not line.strip():
                continue  # Skip empty lines

            if line.startswith("MC[&&]"):  # Handle multiple-choice questions
                parts = line[6:].split("[&&]")
                question = parts[0].strip()
                options = [opt.strip() for opt in parts[1:5]]  # Four options
                correct_answer = options[0]  # Placeholder for correct answer (you can modify this logic)
                questions[f"question_{len(questions) + 1}"] = {
                    "question": question,
                    "options": options,
                    "correct_answer": correct_answer,
                }
            elif line.startswith("SA[%%]"):  # Handle short-answer questions
                parts = line[6:].split("[&&]")
                question = parts[0].strip()
                correct_answer = parts[1].strip() if len(parts) > 1 else ""  # Second part is the answer
                questions[f"question_{len(questions) + 1}"] = {
                    "question": question,
                    "options": [],  # No options for SA
                    "correct_answer": correct_answer,
                }

    except Exception as e:
        print(f"Failed to generate questions: {e}")

    return questions