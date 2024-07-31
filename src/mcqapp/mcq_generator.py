import json
import tempfile
import os
import traceback
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from src.prompt import PROMPT_QUESTIONS, REFINE_PROMPT_QUESTIONS
from src.helper import logger 


class MCQGenerator:
    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name
        self.model = ChatOpenAI(openai_api_key=self.api_key, model_name=self.model_name, temperature=0.5)
        self.ques_gen_chain = load_summarize_chain(
            llm=self.model,
            chain_type="refine",
            verbose=True,
            question_prompt=PROMPT_QUESTIONS,
            refine_prompt=REFINE_PROMPT_QUESTIONS
        )

    def process_file(self, uploaded_file):
        try:
            # Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
            
            # Load the PDF using PyPDFLoader
            loader = PyPDFLoader(temp_file_path)
            docs = loader.load()
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
            documents = text_splitter.split_documents(docs)
            
            # Create a FAISS vector store from documents
            db = FAISS.from_documents(documents, OpenAIEmbeddings())
            
            return db
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            traceback.print_exc()
            return str(e)
        finally:
            # Ensure the temporary file is removed
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def format_mcqs(self, mcqs_json):
        formatted_text = ""

        try:
            mcqs = json.loads(mcqs_json)  # Parse the JSON string into a Python dictionary

            for key, value in mcqs.items():
                formatted_text += f"{key}. {value['mcq']}\n\n"
                options = value['options']
                options_lines = [f"    {key}: {val}" for key, val in options.items()]
                formatted_text += "\n".join(options_lines) + "\n\n"
                formatted_text += f"Correct: [{value['correct']}]\n\n"

        except json.JSONDecodeError:
            formatted_text = mcqs_json  # Fallback if JSON decoding fails

        return formatted_text

    def generate_mcqs(self, db, number, subject, difficulty, response_json, query):
        try:
            result = db.similarity_search(query) if query else db.similarity_search(" ")
            text = " ".join([doc.page_content for doc in result])
            
            formatted_prompt = PROMPT_QUESTIONS.format(
                text=text,
                number=number,
                subject=subject,
                difficulty=difficulty,
                response_json=json.dumps(response_json, indent=4)  # Pretty-print JSON
            )
            
            formatted_prompt_document = Document(page_content=formatted_prompt)
            
            # Use the correct method to generate MCQs
            refined_quiz = self.ques_gen_chain.run(
                input_documents=[formatted_prompt_document],
                subject=subject,
                response_json=response_json,
                difficulty=difficulty,
                number=number
            )
            
            # Format the MCQs output
            formatted_mcqs = self.format_mcqs(refined_quiz)
            
            return formatted_mcqs
        except Exception as e:
            logger.error(f"Error generating MCQs: {e}")
            traceback.print_exc()
            return str(e)
