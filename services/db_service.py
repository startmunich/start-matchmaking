from dotenv import load_dotenv
from langchain_text_splitters import CharacterTextSplitter
import requests
import os
import tempfile

from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


# Read .env file
load_dotenv(override=True)

# Specifies the path of the Chroma vector database, init db
db_path = "./db"
embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory=db_path, embedding_function=embeddings, collection_name="users")

# Specify model
model = ChatOpenAI(model="gpt-3.5-turbo-0125")

# Define custom prompt
prompt_template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.

{context}

Question: {question}

Answer:"""

# Initialize prompt
prompt_template = PromptTemplate.from_template(prompt_template)

llm = prompt_template | model

def add_user_by_conversation(_id: str, user_responses: list):
    db.add_texts(ids=[_id], texts=[str(user_responses)], collection_name="users")


def add_user_by_cv(_id: str, cv_path: str):
    print("Inside add_user_by_cv")
    print("CV Path:", cv_path)

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    auth_header = {'Authorization': f'Bearer {slack_bot_token}'}

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
            # Split extracted text into chunks
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(pages)
            # Extract page_content
            # page_contents = [page.page_content for page in pages]  

        else:
            print("Failed to download the file.")

    # Add split text from CV to the Chroma database 
    db.add_documents(documents=docs, collection_name="users")

    question = input("Ask a question about the CV: ")

    # Perform a similarity search based on the user's question
    context = db.similarity_search(question)

    # Get answer based on the provided context and the user's question
    response = llm.invoke({"question": question, "context": context})
    print("Reponse: ", response.content)






