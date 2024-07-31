from langchain.prompts import PromptTemplate

# Quiz creation prompt
quiz_creation_prompt = """
Text: {text}
You are an expert in creating multiple-choice quizzes. Based on the above text,
generate {number} multiple-choice questions for {subject} students at a {difficulty} difficulty level.
The questions should be directly related to the content of the text and should not introduce any external information.
Ensure that each question is unique and accurate, reflecting the content of the provided text. 
Format your response according to the RESPONSE_JSON example below.

### RESPONSE_JSON
{response_json}
"""

# Prompt templates
PROMPT_QUESTIONS = PromptTemplate(
    input_variables=["text", "number", "subject", "difficulty", "response_json"],
    template=quiz_creation_prompt
)

# Quiz evaluation prompt
quiz_evaluation_prompt = """
You are an expert in English grammar and academic writing. Given the Multiple Choice Quiz for {subject} students below, 
evaluate the relevance and complexity of the questions based on the provided text. 
Provide a concise analysis (up to 50 words) and suggest any necessary adjustments to ensure that 
the questions are appropriate for the students' cognitive and analytical abilities. 
If changes are needed, update the questions to better align with the text.

Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

# Refine prompt questions
REFINE_PROMPT_QUESTIONS = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=quiz_evaluation_prompt,
)
