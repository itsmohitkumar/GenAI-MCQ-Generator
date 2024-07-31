import os
import json
import streamlit as st
from dotenv import load_dotenv
from src.mcqapp.mcq_generator import MCQGenerator
from src.helper import logger 

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Define available models
models = {
    "GPT-3.5 Turbo": "gpt-3.5-turbo",
    "GPT-4": "gpt-4",
    "GPT-4 Turbo": "gpt-4-turbo"
}

# Initialize MCQ Generator
selected_model = st.sidebar.selectbox("Select Model", options=list(models.keys()), index=0)
model_name = models[selected_model]
mcq_generator = MCQGenerator(api_key=API_KEY, model_name=model_name)

# Streamlit app
st.title("🌟 MCQ Generator 🌟")

# Create an empty sidebar initially
with st.sidebar:
    sidebar_placeholder = st.empty()

# Sidebar for API Key input
if not API_KEY:
    with st.sidebar:
        API_KEY = st.text_input("Enter your OpenAI API Key", type="password")
        if API_KEY:
            os.environ["OPENAI_API_KEY"] = API_KEY
else:
    st.sidebar.write("🔑 API Key is set.")

# User inputs with unique keys
uploaded_file = st.file_uploader("📄 Upload a PDF file", type=["pdf"], key="file_uploader_unique")
num_questions = st.number_input("📝 Number of questions", min_value=1, max_value=100, value=10, key="num_questions_unique")
subject = st.text_input("📚 Subject of the MCQs", key="subject_unique")
difficulty = st.selectbox("🔢 Difficulty Level", ["Easy", "Medium", "Hard"], key="difficulty_unique")
query = st.text_input("🔍 Topic or Focus Area for MCQ Generation", placeholder="Enter your query here", key="query_unique")

# Load the response JSON using a relative path
relative_path = os.path.join(os.path.dirname(__file__), "response.json")
if os.path.exists(relative_path):
    with open(relative_path, "r") as file:
        RESPONSE_JSON = json.load(file)
else:
    st.error("Error: RESPONSE_JSON file not found.")
    RESPONSE_JSON = {}

if st.button("🔄 Generate MCQs"):
    if uploaded_file and subject and difficulty:
        db = mcq_generator.process_file(uploaded_file)
        if isinstance(db, str):  # Error message from process_file
            st.error(db)
        else:
            result = mcq_generator.generate_mcqs(db, num_questions, subject, difficulty, RESPONSE_JSON, query)
            if isinstance(result, str) and "Error" in result:
                st.error(result)
            else:
                st.text_area("📝 Generated MCQs", result, height=600, key="mcq_output")
                st.download_button("📥 Download MCQs Text File", result, file_name="mcqs.txt", key="download_button")
    else:
        st.error("⚠️ Please upload a PDF file and fill in all required fields.")