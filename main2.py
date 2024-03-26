import logging
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Read .env file
load_dotenv()

# Initialize model
llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)

# Define the sequence of questions
question = [
    "…"
]

# Initialize chain with placeholder prompt; we'll set the actual prompt dynamically
chain = LLMChain(llm=llm)


### – META CODE –
# Einen Prompt der Konverstion führt im Loop – beeinhaltet alle Fragen fix
# zweiter Prompt, der Antworten verarbeitet und als JSON speichert

# System Prompts
system_prompt = "Context: You're a HR assistant that matches entrepreneurial students within a community to give them sparring partners to solve issues. Your job is to ask questions to those students to get to know them better."

# First message – plain text
first_contact = """Initialising Starties looking for Starties Programm... \n
Hi there 🙋‍♀️, looks like you are using me for the first time. I would love to get to know you a little before I can match potentially helpful people for you (because you might be helpful to others 😉)."
"""

# First questions for information on student – input
first_question = input("In which area would you say you have fairly good expertise?: ")

# Second questions for information on student – input (containing first question information)
prompt_template = f"""A member of our community tells you he/she has expertise in: {first_question}.
Ask a specific follow up-question that helps specifically name and confine the expertise.
Also find one word to describe this expertise or the domain the expertise lies within and give back the response as a json.
Question:
Metaword:
"""
second_question = input(f"What projects or experiences have you already had in which you applied or built up expertise in {metaword}?")

# Third questions for information on student – input (containing second question information)
third_question = input("On a scale from 1-10, how would you rate your Expertise in {metaword}")

# … here things like "in which field do you know an expert" could be thought of

# How can we make this conversation dynamic? e.g. after second questions user corrects the metaword.
# Maybe we can have every time a prompt which has information about all three questions and all three answers and
# updates the inforamtion every time


# CODE when using find a Startie for second time (or after first questions)
mode = "Are you looking for a specific Startie, Expertise, Industry Background or anything else?"
# wie dynamisch können wir hier die Konversation laufen lassen und jeweils die Datenbank nach jeder anfrage checken lassen?



user_prompt = """
This is the previous question you asked: {recent_question}
This is the user's response: {recent_response}

Check whether the user response answers your question sufficiently. In this case, only give a short "YES" in response.
If the question is not answered at all or is completely incomprehensible, formulate an alternative answer that follows up and clarifies open questions.
"""
