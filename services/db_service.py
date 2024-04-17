from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma

# Read .env file
load_dotenv()

# Specifies the path of the Chroma vector database, init db
db_path = "./db"
db = Chroma(persist_directory=db_path, embedding_function=OpenAIEmbeddings(), collection_name="users")


def add_user_by_conversation(_id: str, user_responses: list):
    db.add_texts(ids=[_id], texts=[str(user_responses)], collection_name="users")

# TODO: Read cv from slack conversation using langchain pypdf loader
def add_user_by_cv(_id: str, name:str, cv_path: str):
    pass