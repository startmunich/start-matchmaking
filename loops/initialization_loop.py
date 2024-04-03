from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

from services import cli_service

load_dotenv(override=True)

initialization_message = """Initialising Starties looking for Starties Programm... \n
Hi there 🙋‍♀️, looks like you are using me for the first time. I would love to get to know you a little before I can match potentially helpful people for you (because you might be helpful to others 😉).
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
If the question is not answered at all or is completely incomprehensible, formulate an alternative answer that follows up and clarifies open questions. In this case only answer with your follow up question. Do not stop the conversation flow.
"""

check_prompt = PromptTemplate.from_template(template=check_prompt_template)

# Initialize model and chain
llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
chain = LLMChain(llm=llm, prompt=check_prompt)


counter = -1


def on_message(recent_question, recent_answer, say):
    global counter
    next_question = None

    if counter == -1:
        say(initialization_message)
        counter = 0

    elif recent_question and recent_answer:
        text = chain.invoke({"recent_question": recent_question, "recent_response": recent_answer})["text"]

        if text.upper() != "YES":
            questions.insert(counter + 1, text)

    if counter < len(questions):
        next_question = questions[counter]
        say(next_question)

    counter += 1
    return next_question


