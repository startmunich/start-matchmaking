import logging

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Global variables and module initialization

# Initialize logger
logger = logging.getLogger('start_gpt')

# Read .env file
load_dotenv()

# Initialize model
# TODO: Migrate to more affordable model

llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
# Initialize prompt template
# Wie iniziieren wir den prompt? "Hallo"
# prompt: frage folgenden Dinge ab und speichere sie als json datei

# langchain doku: wie können wir stoppen nachdem json erkannt wurde

prompt_template = """
This is the users answer: {user_input}
"""

# Initialize prompt
prompt = PromptTemplate(input_variables=["user_input"], template=prompt_template)

# Initialize chain
chain = LLMChain(llm=llm, prompt=prompt)

# Answer question
def answer(user_input):
    logger.info(f"answer | {user_input}")

    # Run initialized chain with notion, slack and web results as given context
    return chain.invoke({"user_input": user_input}).get("text")

if __name__ == "__main__":
    while True:
        user_input = input()
        print(answer(user_input))
