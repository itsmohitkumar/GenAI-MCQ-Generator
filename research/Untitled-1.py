# %%
import os
import json
import pandas as pd
import traceback

# %%
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# %%
KEY=os.getenv("OPENAI_API_KEY")
print(KEY)

# %%
#pip install pypdf

# %%
#Retriever And Chain With Langchain
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("/Users/taurangela/Desktop/Github/GenAI-MCQ-Generator |OpenAI |Langchain/data/NEET UG 2024.pdf")
docs = loader.load()
docs

# %%
question_gen = ""

for page in docs:
    question_gen += page.page_content

# %%
question_gen

# %%
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
documents=text_splitter.split_documents(docs)

# %%
documents[:5]

# %%
#pip install faiss-cpu

# %%
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

db=FAISS.from_documents(documents[:30],OpenAIEmbeddings())

# %%
db

# %%
query="DUAL  NATURE OF  MATTER  AND RADIATION"
result=db.similarity_search(query)
result[0].page_content

# %%
RESPONSE_JSON = {
    "1": {
        "mcq": "What is the capital of France?",
        "options": {
            "a": "Berlin",
            "b": "Madrid",
            "c": "Paris",
            "d": "Rome",
        },
        "correct": "c",
    },
    "2": {
        "mcq": "Which planet is known as the Red Planet?",
        "options": {
            "a": "Earth",
            "b": "Mars",
            "c": "Jupiter",
            "d": "Venus",
        },
        "correct": "b",
    },
    "3": {
        "mcq": "What is the chemical symbol for water?",
        "options": {
            "a": "H2O",
            "b": "CO2",
            "c": "O2",
            "d": "NaCl",
        },
        "correct": "a",
    },
}

# %%
quiz_creation_prompt = """
Text: {text}
You are an expert MCQ maker. Given the above text, your job is to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and verify that all questions conform to the text. 
Ensure to format your response like the RESPONSE_JSON below and use it as a guide. \
Make sure to create {number} MCQs.
### RESPONSE_JSON
{response_json}
"""

# %%
from langchain.prompts import PromptTemplate

PROMPT_QUESTIONS = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=quiz_creation_prompt
)

# %%
quiz_evaluation_prompt = """
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students, \
you need to evaluate the complexity of the questions and provide a complete analysis of the quiz. Limit your analysis to at most 50 words. 
If the quiz is not suitable for the students' cognitive and analytical abilities, update the questions and adjust the tone accordingly to match the students' level.
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

# %%
REFINE_PROMPT_QUESTIONS = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=quiz_evaluation_prompt,
)

# %%
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI

# Initialize the model
model = ChatOpenAI(openai_api_key=KEY, model_name="gpt-3.5-turbo", temperature=0.5)

# Load the summarization chain
ques_gen_chain = load_summarize_chain(
    llm=model,
    chain_type="refine",
    verbose=True,
    question_prompt=PROMPT_QUESTIONS,
    refine_prompt=REFINE_PROMPT_QUESTIONS
)

# %%
from langchain.docstore.document import Document

# Example usage
# Define the required variables
text = "Sample text for quiz generation."
number = 3
subject = "Science"
tone = "formal"
response_json = RESPONSE_JSON

# To use the PromptTemplate
formatted_prompt = PROMPT_QUESTIONS.format(
    text=text,
    number=number,
    subject=subject,
    tone=tone,
    response_json=response_json
)

print(formatted_prompt)


# %%
# Wrap the formatted prompt in a Document object
formatted_prompt_document = Document(page_content=formatted_prompt)


# Refine the quiz
refined_quiz = ques_gen_chain.run(
    input_documents=[formatted_prompt_document],  # Use the properly formatted input
    subject=subject,
    response_json=response_json,
    tone=tone,
    number=number
)

print("Refined Quiz:")
print(refined_quiz)


# %%



