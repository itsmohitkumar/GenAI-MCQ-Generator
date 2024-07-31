from langchain.prompts import PromptTemplate

# Quiz creation prompt
quiz_creation_prompt = """
Text: {text}
You are an expert MCQ maker. Given the above text, your job is to \
create a quiz of {number} multiple choice questions for {subject} students at a {difficulty} difficulty level. 
Make sure the questions are not repeated and verify that all questions conform to the text. 
Ensure to format your response like the RESPONSE_JSON below and use it as a guide. \
Make sure to create {number} MCQs.
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
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students, \
you need to evaluate the complexity of the questions and provide a complete analysis of the quiz. Limit your analysis to at most 50 words. 
If the quiz is not suitable for the students' cognitive and analytical abilities, update the questions and adjust the difficulty level accordingly to match the students' level.
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

# Refine prompt questions
REFINE_PROMPT_QUESTIONS = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=quiz_evaluation_prompt,
)
