import json
import tempfile
import os
import traceback
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from src.prompt import PROMPT_QUESTIONS, REFINE_PROMPT_QUESTIONS
from src.helper import logger

# Load environment variables
load_dotenv()

class MCQGenerator:
    def __init__(self, openai_key=None, google_key=None, model_name="google"):
        self.openai_key = openai_key
        self.google_key = google_key
        self.model_name = model_name
        
        if self.model_name == "google":
            self.model = ChatGoogleGenerativeAI(model="gemini-pro", api_key=self.google_key)
            self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        elif self.model_name in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]:
            self.model = ChatOpenAI(openai_api_key=self.openai_key, model_name=self.model_name, temperature=0.5)
            self.embeddings = OpenAIEmbeddings()
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")
        
        self.ques_gen_chain = load_summarize_chain(
            llm=self.model,
            chain_type="refine",
            verbose=True,
            question_prompt=PROMPT_QUESTIONS,
            refine_prompt=REFINE_PROMPT_QUESTIONS
        )

    def format_mcqs(self, mcqs_json):
        formatted_text = ""

        try:
            mcqs = json.loads(mcqs_json)

            if isinstance(mcqs, dict):
                for key, value in sorted(mcqs.items(), key=lambda x: int(x[0])):
                    formatted_text += f"{key}. {value['mcq']}\n\n"
                    options = value['options']
                    options_lines = [f"    {opt}: {text}" for opt, text in options.items()]
                    formatted_text += "\n".join(options_lines) + "\n\n"
                    formatted_text += f"Correct: [{value['correct']}]\n\n"
            else:
                logger.warning("Unexpected format in MCQs response")
                formatted_text = mcqs_json

        except json.JSONDecodeError:
            logger.error("Failed to decode MCQs JSON")
            formatted_text = mcqs_json

        return formatted_text

    def process_file(self, uploaded_file):
        try:
            # Save the uploaded file to a temporary location
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            if file_extension == ".pdf":
                # Load the PDF using PyPDFLoader
                loader = PyPDFLoader(temp_file_path)
                docs = loader.load()
            elif file_extension == ".txt":
                # Load the TXT file
                with open(temp_file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                # Convert the text into a list of Document objects
                docs = [Document(page_content=text)]
            else:
                raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")

            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
            documents = text_splitter.split_documents(docs)

            # Create a FAISS vector store from documents
            db = FAISS.from_documents(documents, self.embeddings)

            return db
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            traceback.print_exc()
            return str(e)
        finally:
            # Ensure the temporary file is removed
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def generate_mcqs(self, db, number, subject, difficulty, response_json, query):
        try:
            result = db.similarity_search(query) if query else db.similarity_search(" ")
            text = " ".join([doc.page_content for doc in result])
            
            formatted_prompt = PROMPT_QUESTIONS.format(
                text=text,
                number=number,
                subject=subject,
                difficulty=difficulty,
                response_json=json.dumps(response_json, indent=4)
            )
            
            if self.model_name == "google":
                # Use invoke method for Google model
                response = self.model.invoke(formatted_prompt)
                refined_quiz = getattr(response, 'content', '')  # Safely extract content from the response
            else:
                refined_quiz = self.ques_gen_chain.run(
                    input_documents=[Document(page_content=formatted_prompt)],
                    subject=subject,
                    response_json=response_json,
                    difficulty=difficulty,
                    number=number
                )
            
            formatted_mcqs = self.format_mcqs(refined_quiz)
            
            return formatted_mcqs
        except Exception as e:
            logger.error(f"Error generating MCQs: {e}")
            traceback.print_exc()
            return str(e)
