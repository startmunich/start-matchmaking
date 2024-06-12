import re

from dotenv import load_dotenv
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_core.chat_history import BaseChatMessageHistory
import requests
import os
import tempfile

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
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
    index_name="chunk_index",
    node_label="Chunk",
    text_node_properties=["text"],
    embedding_node_property="embedding",
)


# Create a new chunk in the database
def create_chunk(chunk):
    print("db_service | create_chunk")

    query = f"""
    CREATE (c:Chunk {{text: '{chunk.text}', startie_id: '{chunk.startie_id}'}})
    RETURN id(c)
    """

    return store.query(query)[0]["id(c)"]


# Connect a chunk to a Startie
def connect_chunk_to_startie(chunk_id, startie_id):
    print(f"db_service | connect_chunk_to_startie | {chunk_id} | {startie_id}")

    query = f"""
    MATCH (c:Chunk) WHERE ID(c) = {chunk_id}
    MATCH (s:Startie) WHERE ID(s) = {startie_id}
    CREATE (c)-[:BELONGS_TO]->(s)
    """

    print(query)

    store.query(query)


# Create a new Startie
def create_startie(startie, chunks):
    print("db_service | create_startie")

    query = f"""
        CREATE (s:Startie {{slack_id: '{startie.slack_id}', name: '{startie.name}'}})
        RETURN id(s)
        """

    result = store.query(query)
    print(f"result: {result}")
    startie_id = result[0]["id(s)"]

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
    RETURN id(s)
    """

    result = store.query(query)
    print(f"result: {result}")
    startie_id = result[0]["id(s)"]

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

    print(query)

    result = store.query(query)
    print(f"result: {result}")

    return result


# Find a Startie by their Slack ID
def find_startie_by_id(slack_id):
    print(f"db_service | find_startie_by_id | {slack_id}")

    query = f"""
    MATCH (s:Startie {{slack_id: '{slack_id}'}})
    RETURN s
    """

    return store.query(query)


def sanitize_chunk(text):
    # Escape single quotes
    text = text.replace("'", "\\'")
    # Escape double quotes
    text = text.replace('"', '\\"')
    # Escape backslashes
    text = text.replace("\\", "\\\\")
    # Escape newlines and carriage returns
    text = text.replace("\n", "\\n").replace("\r", "\\r")
    # Escape curly braces
    text = text.replace("{", "\\{").replace("}", "\\}")
    # Escape square brackets
    text = text.replace("[", "\\[").replace("]", "\\]")
    # Escape parentheses
    text = text.replace("(", "\\(").replace(")", "\\)")
    # Optional: Escape other characters if needed
    text = re.sub(r'([;%$#&*])', r'\\\1', text)
    return text


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
            chunks = [Chunk(text=sanitize_chunk(doc.page_content), startie_id=_id) for doc in docs]
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
