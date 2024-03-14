import logging

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
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
prompt_template = """ 
It is December 2023. You are StartGPT, an assistant for question-answering tasks. Users reach out to you only via Slack. You serve a student led organization START Munich. The context you get will be from our Notion and/or Slack, and/or our Website. Use the following pieces of retrieved context to answer the question. You can use either one of the sources (context) or combine them. You decide what's more useful. If you don't know the answer, just say that you don't know.
Question: {question}
Notion result: {notion} 
Slack result: {slack}
Website result: {web}

You don't need to mention where you got the information from.
"""

# Initialize prompt
prompt = PromptTemplate(input_variables=["question", "notion", "slack", "web"], template=prompt_template)

# Initialize chain
chain = LLMChain(llm=llm, prompt=prompt)


# Answer question
def answer(question):
    logger.info(f"answer | {question}")

    result_notion = ""
    result_slack = ""
    result_web = ""

    # Run initialized chain with notion, slack and web results as given context
    return chain.run(question=question, notion=result_notion, slack=result_slack, web=result_web)


if __name__ == "__main__":
    while True:
        question = input()
        print(answer(question))