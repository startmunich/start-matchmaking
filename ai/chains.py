from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from ai.prompts import router_prompt, add_user_prompt, conversation_prompt, update_user_prompt, search_query_prompt
from services import db_service

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)


def build_runnable(prompt):
    return RunnableWithMessageHistory(
        runnable=ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}"),
        ]
        ) | llm | StrOutputParser(),
        get_session_history=db_service.get_session_history,
        input_messages_key="user_input",
        history_messages_key="history",
    )


add_user_chain = build_runnable(add_user_prompt)
update_user_chain = build_runnable(update_user_prompt)
search_query_chain = build_runnable(search_query_prompt)
conversation_chain = build_runnable(conversation_prompt)
router_chain = build_runnable(router_prompt)


def route(context, config):
    result = router_chain.invoke(context, config)

    if "1" in result:
        print("route 1 -> add user")
        # TODO: Add the user to the system
        return add_user_chain.invoke(context, config)
    elif "2" in result:
        print("route 2 -> update user")
        # TODO: Update the user's CV
        return update_user_chain.invoke(context, config)
    elif "3" in result:
        print("route 3 -> search query")
        # TODO: Find the best match for the user
        matches = db_service.store.similarity_search_with_score(context["user_input"], k=1)
        context["matches"] = matches
        print(context["matches"])
        return search_query_chain.invoke(context, config)
    elif "4" in result:
        print("route 4 -> conversation")
        return conversation_chain.invoke(context, config)
    else:
        print("Invalid route: ", result)


def on_message(message, say, cv_upload=None):
    print("chains | on_message")

    user_input = message["text"]

    if not user_input and cv_upload:
        user_input += "CV uploaded"

    context = {
        "user_exists": db_service.find_startie_by_id(message["user"]) is not [],
        "user_input": user_input,
        "cv_upload": cv_upload is not None,
        "matches": []
    }

    config = {'configurable': {'session_id': message["user"]}}

    print("context: ", context)
    print("config: ", config)

    result = route(context, config)
    if result and type(result) is str:
        say(result)
