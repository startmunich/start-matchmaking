from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

from services import db_service

load_dotenv(override=True)

# Define the questions to be asked in this loop
questions = [
    "What kind of STARTie are you looking for? (e.g. 'Someone with experience in Consulting')",
    "What specific skills or expertise should this person have?",
    "What projects or experiences should they have worked on?",
    "Anything else you would like to add about your ideal STARTie?"
]

# Define the prompt templates
check_prompt_template_str = """
This is the previous question you asked: {recent_question}
This is the user's response: {recent_response}

Check whether the user response answers your question sufficiently. In this case, only give a short "YES" in response.
If the question is not answered at all or is completely incomprehensible, only answer with a follow-up question for clarification.
"""

json_prompt_template_str = """
I give you a list of questions and a list of answers from a conversation with a matchmaking bot trying to get information about the ideal match for a user:
These are the questions: {questions}
These are the answers: {user_responses}

Output a JSON format with the following keys: "desired_skills", "desired_expertise", "desired_projects", "additional_info".
Use the information from the user responses in context with the questions dynamically to fill the values.
"""

# Initialize the prompts
check_prompt = PromptTemplate(input_variables=["recent_question", "recent_response"], template=check_prompt_template_str)
json_prompt = PromptTemplate(input_variables=["questions", "user_responses"], template=json_prompt_template_str)

# Initialize the model and chain
llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)

chain = LLMChain(llm=llm, prompt=check_prompt)
chain_two = LLMChain(llm=llm, prompt=json_prompt)

# Data structure to hold the conversation data
conversation_data = {
    "questions": [],
    "user_responses": [],
    "gpt_text": []
}

counter = 0

def on_message(user_id, recent_question, recent_answer, say):
    global counter
    global chain

    next_question = None

    # If recent question and recent answer given, run chain (using check_prompt)
    if recent_question and recent_answer:
        # Get response from chain (using check_prompt) -> either a follow-up question or a "YES"
        text = chain.invoke({"recent_question": recent_question, "recent_response": recent_answer})["text"]

        # Append the recent question, recent answer and response text to the conversation_data dictionary
        conversation_data["questions"].append(recent_question)
        conversation_data["user_responses"].append(recent_answer)
        conversation_data["gpt_text"].append(text)

        # Check if response is "YES" -> if not, insert the follow-up question into the questions list
        if text.upper() != "YES":
            questions.insert(counter, text)

    # If questions are available, ask the next question
    if counter < len(questions):
        next_question = questions[counter]
        say(next_question)
    else:
        # If no more questions are available, say "Thank you for your time" and print the conversation data
        say("Looking for your ideal STARTie...")
        print("This is the conversation data:\n")
        print(conversation_data)

        # Create a summary of the conversation data
        json_formatted_data = chain_two.invoke({"user_responses": conversation_data["user_responses"], "questions": conversation_data["questions"]})["text"]

        print("\nThis will be added to the db:\n")
        print(json_formatted_data)
        # Add the summary to the database
        db_service.add_user_preferences(_id=user_id, user_responses=[json_formatted_data])

    # Increment the counter and return the next question
    counter += 1
    return next_question
