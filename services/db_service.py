from dotenv import load_dotenv
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_text_splitters import CharacterTextSplitter
import requests
import os
import tempfile

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from services import slack_service

# Read .env file
load_dotenv(override=True)

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

# Initialize the Neo4jVector store
store = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name="startie_index",
    node_label="Startie",
    text_node_properties=["cv", "skills"],
    embedding_node_property="embedding",
)


# Create a new Startie
def create_startie(startie):
    query = f"""
    CREATE (s:Startie {{slack_id: '{startie.slack_id}', name: '{startie.name}', skills: '{startie.skills}', cv: '{startie.cv}'}})
    """

    print("Query:", query)
    store.query(query)
    return startie


# Update an existing Startie
def update_startie(startie):
    query = f"""
    MATCH (s:Startie {{slack_id: '{startie.slack_id}'}})
    SET s.name = '{startie.name}', s.skills = '{startie.skills}', s.cv = '{startie.cv}'
    """

    store.query(query)
    return startie


# Save a Startie to the database (create or update)
def save_startie(startie):
    if find_startie_by_id(startie.slack_id):
        return update_startie(startie)
    else:
        return create_startie(startie)


# Find a Startie by their Slack ID
def find_startie_by_id(slack_id):
    query = f"""
    MATCH (s:Startie {{slack_id: '{slack_id}'}})
    RETURN s
    """

    result = store.query(query)
    print("Type of result:", type(result))
    print("Result:", result)
    return result



# Add a Startie by their CV
def add_startie_by_cv(_id: str, cv_path: str):
    print("Inside add_user_by_cv")

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    auth_header = {'Authorization': f'Bearer {slack_bot_token}'}

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:

        # Download PDF file to the temporary directory
        pdf_filename = cv_path.split('/')[-1]
        pdf_path = os.path.join(temp_dir, pdf_filename)
        response = requests.get(cv_path, headers=auth_header)

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        # Check if the file exists at the specified path
        if os.path.exists(pdf_path):

            # Extract text from the downloaded PDF using Langchain PyPDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            print(pages)
            # Split extracted text into chunks 
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(pages)
            # Extract page_content
            # page_contents = [page.page_content for page in pages]

            # Create a Startie object from slack_service, set cv of the startie and store in the database
            startie = slack_service.find_startie_by_id(_id)
            startie.cv = "\n".join([doc.page_content for doc in docs])
            save_startie(startie)
            return startie.cv

        else:
            print("Failed to download the file.")
            return None


# Temporary session store -> in memory, replace either with Neo4j or Redis
session_store = {}


# Get the chat history for a session
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]
