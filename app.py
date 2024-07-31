import os
import json
import streamlit as st
from dotenv import load_dotenv
from src.mcqapp.mcq_generator import MCQGenerator
from src.helper import logger

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# Set project name and environment variables
PROJECT_NAME = "Mcq Generator"
os.environ["LANGCHAIN_PROJECT"] = PROJECT_NAME
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY

# Define available models
models = {
    "Google Gemini": "google",
    "GPT-3.5 Turbo": "gpt-3.5-turbo",
    "GPT-4": "gpt-4",
    "GPT-4 Turbo": "gpt-4-turbo"
}

def load_response_json():
    with open("response.json", "r") as file:
        return json.load(file)

def main():
    st.set_page_config(page_title="MCQ Generator", page_icon=":books:")
    st.title("MCQ Generator :books:")

    st.sidebar.header("Configuration")

    # Use API keys from environment variables or prompt for input
    openai_key = OPENAI_API_KEY or st.sidebar.text_input("OpenAI API Key", type="password")
    google_key = GOOGLE_API_KEY or st.sidebar.text_input("Google API Key", type="password")
    model_name = st.sidebar.selectbox("Model Name", list(models.keys()), index=0)  # Default to Google Gemini
    
    # Load response JSON
    response_json = load_response_json()

    # File upload
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "txt"])
    if uploaded_file is None:
        st.warning("Please upload a file.")
        return

    # Determine file type based on the uploaded file extension
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in ["pdf", "txt"]:
        st.error("Unsupported file type.")
        return

    # MCQ Generator setup
    if model_name == "google" and not google_key:
        st.error("Please provide your Google API key.")
        return
    elif model_name in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"] and not openai_key:
        st.error("Please provide your OpenAI API key.")
        return

    mcq_generator = MCQGenerator(openai_key=openai_key, google_key=google_key, model_name=models[model_name])

    # Processing file
    with st.spinner("Processing file... :hourglass:"):
        db = mcq_generator.process_file(uploaded_file)
        if isinstance(db, str):
            st.error(f"Error processing file: {db}")
            return

    # Integrated settings form
    with st.form(key='mcq_form'):
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=100, value=10)
        subject = st.text_input("Subject", value="General Knowledge")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        query = st.text_area("Query", placeholder="Enter your query here")

        generate_button = st.form_submit_button(label='Generate MCQs')

    if generate_button:
        with st.spinner("Generating MCQs... :page_with_curl:"):
            mcqs = mcq_generator.generate_mcqs(db, num_questions, subject, difficulty, response_json, query)
            st.subheader("Generated MCQs ✏️")
            st.markdown(mcqs)  # Use markdown to preserve formatting
            
            # Provide a download button for the generated MCQs
            st.download_button(
                label="Download MCQs",
                data=mcqs,
                file_name="generated_mcqs.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
