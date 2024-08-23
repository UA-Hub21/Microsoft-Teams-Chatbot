import os
from dotenv import load_dotenv
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
load_dotenv()

class Memory_Management:
    user_id_list = {
        "29:1ENqfv91NRZOMZKzXWL1JY7nVXQT4WGgO8ra28_63Z0gRTWm4X5QzkKI-arR_N9HQU3PutAijMuAJR6zV3DciaQ" : "tthamerica 1.3",
        "29:10woqVkAB_BZTXPQxIqOcaWBhhTooESlSpOlgJy--ZmXOn8OOofHjPWFxfsJtUd0Vj4K-TFVoK3m60WImg1dWAg" : "Dixon Joe"
            }
    class JSON_Parser(BaseModel):
        Action: str = Field(description="Action represents the task to be done in the database like update, insert, delete, etc..")
        Data: str = Field(description="Data represents the features or columns on which the task should be performed.")
        User_ID: str = Field(description="ID represents the user id mentioned in the query. Reference Examples: A129336, U5661979, A3371209")
    
    @classmethod
    def runnable(cls):
        llm = ChatVertexAI(model="gemini-1.5-flash-001", temperature=0, max_tokens=None,max_retries=6, stop=None)
        output_parser = JsonOutputParser(pydantic_object=Memory_Management.JSON_Parser)
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are an excellent data identifier. Your task is to identify the Action, Data and User_ID present in the given query.
                NOTE: Note that TeamsConversationBot is not the User_ID.
                User_ID Reference Examples: A129336, U5661979, A3371209
                Format Instructions: {format_instructions}
                """,

            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}"),
        ]
    )
        runnable = prompt | llm | output_parser
        return runnable

    store = {}
    @classmethod
    def get_session_history(cls,session_id: str) -> BaseChatMessageHistory:
        if session_id not in cls.store:
            cls.store[session_id] = ChatMessageHistory()
        else:
            if len(cls.store[session_id].messages) > 2:
                mess=cls.store[session_id].messages[-2:]
                cls.store[session_id].clear()
                cls.store[session_id].add_messages(mess)
        return cls.store[session_id]

    @classmethod
    def message_history(cls):
        runnable = cls.runnable()
        with_message_history = RunnableWithMessageHistory(
        runnable,
        cls.get_session_history,
        input_messages_key="query",
        history_messages_key="history",
    )
        return with_message_history
    
    @classmethod
    def get_response(cls, query, response):
        if response == 1:
            with_message_history = cls.message_history()
            output_parser = JsonOutputParser(pydantic_object=Memory_Management.JSON_Parser)
            response = with_message_history.invoke(
                {"query":query, "format_instructions": output_parser.get_format_instructions()},
                config={"configurable": {"session_id": "abc123"}},)
            user_id = response["User_ID"]
            return user_id, response
        if response == 2:
            pass
        
    db = {}
    @classmethod
    def store_db(cls, user_id, response, message_id, name, check_id, query):
        cls.db[user_id] = response
        cls.db[user_id]["Message_id"] = message_id
        cls.db[user_id]["name"] = name
        cls.db[user_id]["check_id"] = check_id
        cls.db[user_id]["query"] = query
        print("Data Added: ")
        print(cls.db)
        
    @classmethod
    def get_data(cls, user_id):
        return cls.db[user_id]
    
    @classmethod
    def del_data(cls, user_id):
        del cls.db[user_id]
        print("Data Deleted: ")
        print(cls.db)

        
    