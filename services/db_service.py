from dotenv import load_dotenv
import requests
import os
import tempfile



from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader

# Read .env file
load_dotenv(override=True)

# Specifies the path of the Chroma vector database, init db
db_path = "./db"
db = Chroma(persist_directory=db_path, embedding_function=OpenAIEmbeddings(), collection_name="users")


def add_user_by_conversation(_id: str, user_responses: list):
    db.add_texts(ids=[_id], texts=[str(user_responses)], collection_name="users")

# TODO: Read cv from slack conversation using langchain pypdf loader
def add_user_by_cv(_id: str, cv_path: str):
    print("Inside add_user_by_cv")
    print("CV Path:", cv_path)

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    auth_header = {'Authorization': f'Bearer {slack_bot_token}'}

    # Download PDF file locally to specific location
    # pdf_filename = cv_path.split('/')[-1]
    # pdf_path = f'/Users/yasinozturk/Downloads/matchmaking testing/{pdf_filename}'
    # response = requests.get(cv_path, headers=auth_header)
    # print(response)
    # with open(pdf_path, 'wb') as f:
    #     f.write(response.content)

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print("Temporary Directory Path:", temp_dir)
        
        # Download PDF file to the temporary directory
        pdf_filename = cv_path.split('/')[-1]
        pdf_path = os.path.join(temp_dir, pdf_filename)
        print("Temporary PDF Path:", pdf_path)
        
        response = requests.get(cv_path, headers=auth_header)
        print("Response Status Code:", response.status_code)
        
        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        # Check if the file exists at the specified path
        if os.path.exists(pdf_path):
            print("File downloaded successfully:", pdf_path)
            
            # Extract text from the downloaded PDF using Langchain PyPDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            print(pages)
        else:
            print("Failed to download the file.")


    # Extract text from the downloaded PDF using vanilla PyPDF
    # reader = PdfReader(pdf_path)
    # number_of_pages = len(reader.pages)
    # page = reader.pages[0]
    # text = page.extract_text()
    # print(text)


