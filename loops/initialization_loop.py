from langchain.chains.llm import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

from services import chat_service


initialization_message = """Initialising Starties looking for Starties Programm... \n
Hi there 🙋‍♀️, looks like you are using me for the first time. I would love to get to know you a little before I can match potentially helpful people for you (because you might be helpful to others 😉)."
"""

questions = [
    "In which area would you say you have fairly good expertise?",
    "What projects or experiences have you already had in which you applied or built up this expertise?",
    "On a scale from 1-10, how would you rate your expertise in this field?"
]


check_prompt_template = """
This is the previous question you asked: {recent_question}
This is the user's response: {recent_response}

Check whether the user response answers your question sufficiently. In this case, only give a short "YES" in response.
If the question is not answered at all or is completely incomprehensible, formulate an alternative answer that follows up and clarifies open questions.
"""

check_prompt = PromptTemplate.from_template(template=check_prompt_template)

# Initialize model and chain
llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
chain = LLMChain(llm=llm, prompt=check_prompt)


def run():
    chat_service.write_message(initialization_message)

    counter = 0

    while counter < 3:
        recent_question = questions[counter]
        recent_answer = chat_service.get_answer(recent_question)
        counter += 1
        print(chain.invoke({"recent_question": recent_question, "recent_response": recent_answer}))
