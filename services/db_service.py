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
<<<<<<< HEAD
=======
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_experimental.text_splitter import SemanticChunker

>>>>>>> 799966017a87821b807745524338899c6cf4e249

from model.chunk import Chunk
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


# Create a new chunk in the database
def create_chunk(chunk):
    print("db_service | create_chunk")

    query = f"""
    CREATE (c:Chunk {{text: '{chunk.text}'}})
    RETURN id(c)
    """

    return store.query(query)


# Connect a chunk to a Startie
def connect_chunk_to_startie(chunk_id, startie_id):
    print(f"db_service | connect_chunk_to_startie | {chunk_id} | {startie_id}")

    query = f"""
    MATCH (c:Chunk {{id: '{chunk_id}'}})
    MATCH (s:Startie {{id: '{startie_id}'}})
    MERGE (c)-[:BELONGS_TO]->(s)
    """

    store.query(query)


# Create a new Startie
def create_startie(startie, chunks):
    print("db_service | create_startie")

    query = f"""
        CREATE (s:Startie {{slack_id: '{startie.slack_id}', name: '{startie.name}'}})
        RETURN id(s)
        """

    startie_id = store.query(query)

    for chunk in chunks:
        chunk_id = create_chunk(chunk)
        connect_chunk_to_startie(chunk_id, startie_id)

    return startie_id


# Update an existing Startie
def update_startie(startie, chunks):
    print("db_service | update_startie")

    # Remove all existing chunks
    query = f"""
    MATCH (s:Startie {{slack_id: '{startie.slack_id}'}})-[:BELONGS_TO]->(c:Chunk)
    DETACH DELETE c
    """

    startie_id = store.query(query)

    # Add new chunks to startie
    for chunk in chunks:
        chunk_id = create_chunk(chunk)
        connect_chunk_to_startie(chunk_id, startie_id)

    return startie_id


# Save a Startie to the database (create or update)
def save_startie(startie, chunks):
    print("db_service | save_startie")

    if find_startie_by_id(startie.slack_id):
        return update_startie(startie, chunks)
    else:
        return create_startie(startie, chunks)


# Find a Startie by their chunk
def find_startie_by_chunk(chunk):
    print(f"db_service | find_startie_by_chunk | {chunk}")

    query = f"""
    MATCH (c:Chunk {{text: '{chunk.text}'}})-[:BELONGS_TO]->(s:Startie)
    RETURN s
    """

    return store.query(query)


# Find a Startie by their Slack ID
def find_startie_by_id(slack_id):
    print(f"db_service | find_startie_by_id | {slack_id}")

    query = f"""
    MATCH (s:Startie {{slack_id: '{slack_id}'}})
    RETURN s
    """

    return store.query(query)


# Add a Startie by their CV
def add_startie_by_cv(_id: str, cv_path: str):
    print(f"db_service | add_startie_by_cv | {_id}, {cv_path}")

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
            # Combine all pages' content into a single string
            full_text = "\n".join([page.page_content for page in pages])
            print(full_text)
            # Split extracted text into chunks 
            # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            # docs = text_splitter.split_documents(pages)
            text_splitter = SemanticChunker(OpenAIEmbeddings())
            docs = text_splitter.create_documents([full_text])
            print(docs[0].page_content)
            print(len(docs))
            # Extract page_content
            # page_contents = [page.page_content for page in pages]

            # Create a Startie object from slack_service, set cv of the startie and store in the database
            startie = slack_service.find_startie_by_id(_id)
            chunks = [Chunk(text=doc.page_content) for doc in docs]
            save_startie(startie, chunks)
            return startie

        else:
            print("Failed to download the file.")
            return None


# Temporary session store -> in memory, replace either with Neo4j or Redis
session_store = {}


# Get the chat history for a session
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    print("db_service | get_session_history")

    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]
