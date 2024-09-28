import asyncio
import re

from dotenv import load_dotenv
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_community.vectorstores import SurrealDBStore
from langchain_core.chat_history import BaseChatMessageHistory
from utils import download_temp
import requests
import os
import tempfile

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from surrealdb import Surreal
from model.chunk import Chunk
from model.startie import Startie
from services import slack_service

# Read .env file
load_dotenv(override=True)

SURREALDB_URL = os.environ.get("SURREALDB_URL", "ws://localhost:8000/rpc")
SURREALDB_USERNAME = os.environ.get("SURREALDB_USERNAME", "root")
SURREALDB_PASSWORD = os.environ.get("SURREALDB_PASSWORD", "root")

# Initialize SurrealDB client
db = Surreal(SURREALDB_URL)

# Initialize the SurrealDBStore for vector operations
store = SurrealDBStore(
    dburl=SURREALDB_URL,
    embedding_function=OpenAIEmbeddings(),
    db_user=SURREALDB_USERNAME,
    db_pass=SURREALDB_PASSWORD,
    ns="langchain",
    db="database",
    collection="chunks"
)

async def init_db():
    await db.connect()
    await db.signin({"user": SURREALDB_USERNAME, "pass": SURREALDB_PASSWORD})
    await db.use("langchain", "database")
    await store.initialize()
    await define_indexes()
    print("Database initialized and indexes created.")

async def define_indexes():
    # Only create index on startie_id
    await db.query("DEFINE INDEX idx_startie_id ON TABLE chunks FIELDS startie_id")
    print("Indexes created successfully.")

async def create_chunk(chunk):
    print("db_service | create_chunk")
    return await store.aadd_texts([chunk.text], metadatas=[{"startie_id": chunk.startie_id}])

async def create_startie(startie, chunks):
    print("db_service | create_startie")
    result = await db.create("startie", {
        "slack_id": startie.slack_id,
        "name": startie.name
    })
    startie_id = result[0]['id']

    for chunk in chunks:
        await create_chunk(chunk)

    return startie

async def update_startie(startie, chunks):
    print("db_service | update_startie")
    await store.adelete(where={"startie_id": startie.slack_id})

    for chunk in chunks:
        await create_chunk(chunk)

    return startie


async def save_startie(_slack_id, chunks):
    print("db_service | save_startie")
    existing_startie = await find_startie_by_id(_slack_id)
    if existing_startie:
        return await update_startie(existing_startie, chunks)
    else:
        return await create_startie(existing_startie, chunks)

async def find_startie_by_id(slack_id):
    print(f"db_service | find_startie_by_id | {slack_id}")
    result = await db.query(f"SELECT * FROM startie WHERE slack_id = $slack_id", {
        "slack_id": slack_id
    })
    return result[0]['result'][0] if result and result[0]['result'] else None


async def add_startie_by_cv(_id: str, cv_path: str):
    print(f"db_service | add_startie_by_cv | {_id}, {cv_path}")
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    auth_header = {'Authorization': f'Bearer {slack_bot_token}'}
    pdf_path = await download_temp(cv_path, auth_header)

        # if os.path.exists(pdf_path):
        #     loader = PyPDFLoader(pdf_path)
        #     pages = loader.load_and_split()
        #     full_text = "\n".join([page.page_content for page in pages])

        #     text_splitter = SemanticChunker(OpenAIEmbeddings())
        #     docs = text_splitter.create_documents([full_text])

        #     startie = await slack_service.find_startie_by_id(_id)
        #     chunks = [Chunk(text=doc.page_content, startie_id=_id) for doc in docs]
        #     await save_startie(startie, chunks)
        #     return startie

    if os.path.exists(pdf_path):
        loader = PyPDFLoader(pdf_path)
        pages = await asyncio.to_thread(loader.load_and_split)
        full_text = "\n".join([page.page_content for page in pages])

        text_splitter = SemanticChunker(OpenAIEmbeddings())
        docs = await asyncio.to_thread(text_splitter.create_documents, [full_text])

        #startie = await slack_service.find_startie_by_id(_id)
        chunks = [Chunk(text=doc.page_content, startie_id=_id) for doc in docs]
        return await save_startie(_id, chunks)

    else:
        print("Failed to download the file.")
        return None


async def get_chunks_for_startie(startie_id):
    print(f"db_service | get_chunks_for_startie | {startie_id}")
    result = await db.query(f"SELECT * FROM chunks WHERE startie_id = $startie_id", {
        "startie_id": startie_id
    })
    return result[0]['result'] if result and result[0]['result'] else None


async def similarity_search_excluding_user(query, config, k=1):
    slack_id = config['configurable']['session_id']
    print(f"db_service | similarity_search_excluding_user | query: {query}, slack_id: {slack_id}, k: {k}")

    all_matches = await store.asimilarity_search_with_score(query, k=k+1)

    filtered_matches = [
        (match, score) for match, score in all_matches
        if match.metadata.get('startie_id') != slack_id
    ][:k]

    return filtered_matches

session_store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    print("db_service | get_session_history")
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]
