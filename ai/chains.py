from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from ai.prompts import router_prompt, add_user_prompt, conversation_prompt, update_user_prompt, search_query_prompt
from model import startie
from services import db_service

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

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

async def route(context, config):
    result = await router_chain.ainvoke(context, config)

    if "1" in result:
        print("route 1 -> add user")
        return await add_user_chain.ainvoke(context, config)
    elif "2" in result:
        print("route 2 -> update user")
        return await update_user_chain.ainvoke(context, config)
    elif "3" in result:
        print("route 3 -> search query")
        matches = await db_service.similarity_search_excluding_user(context["user_input"], config, k=1)
        print("config", config)
        context["matches"] = matches
        print("matches", context["matches"])
        return await search_query_chain.ainvoke(context, config)
    elif "4" in result:
        print("route 4 -> conversation")
        return await conversation_chain.ainvoke(context, config)
    else:
        print("Invalid route: ", result)

async def on_message(message, say, cv_upload=None):
    print("chains | on_message")
    user_input = message["text"]

    if not user_input and cv_upload:
        user_input += "CV uploaded"

    startie = await db_service.find_startie_by_id(message["user"])
    user_exists = startie is not None
    
    context = {
        "user_exists": user_exists,
        "user_input": user_input,
        "cv_upload": cv_upload is not None,
        "matches": []
    }

    config = {'configurable': {'session_id': message["user"]}}

    print("context: ", context)
    print("config: ", config)

    try:
        result = await route(context, config)
        if result and isinstance(result, str):
            await say(result)
    except Exception as e:
        print("Error: ", e)
        await say("Sorry, an error occurred. 😢 My admin has been notified.")

