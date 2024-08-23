import os
import requests
from monitoring import monitor
from dotenv import load_dotenv 
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

class Tools:
    @staticmethod
    @tool
    def Database_Queries(input: str) -> str:
        """"
        ****Database Modification Queries for Crew Members***
        
        This tool is designed to handle requests for modifying existing data in a database related to crew members, with a focus on updating, adding, or removing specific adjustments based on their user ID. 
        The tool recognizes a variety of query formats and phrasing.

        Example Queries:
        "Can someone please remove all the PTC & LPV adjustments only for U112712, please?"
        "Please add all the AMV & DER adjustments for K234667?"
        "Modify the SWQ & GCD adjustments in the database. My User ID is Y762134."
        "Can someone please add all the PTC & LPV adjustments only for U112712, please?"
        "Please add the PTC & LPV adjustments for user ID U112712."
        "Please remove the GEEW adjustments for H67543."
        
        ***VERY IMPORTANT: You are supposed to respond with number 1.***
        """
        return "1"

    @staticmethod
    @tool
    def Irrelevant(input: str) -> str:
        """
        This tool is specifically designed to handle queries that are not related to updating the database or requesting confirmation of actions. 
        It focuses on identifying and responding to queries that fall outside the scope of database modifications.
        
        ***VERY IMPORTANT: You are supposed to respond with number 2.***
        """
        return "2"
    
    
    
class Agents(Tools):
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv("api_key")
        self.llm = ChatVertexAI(model="gemini-1.5-flash-001", temperature=0, max_tokens=None,max_retries=6, stop=None)
        self.tools = [Tools.Database_Queries, Tools.Irrelevant]
    
    def Response(self, query):
        system = """
        You are a helpful assistant specialized in identifying queries related to United Airlines.
        You have access to the following tools:

        1 - Database_Queries
        2 - Irrelevant

        ***VERY IMPORTANT: You are supposed to respond with any one number - 1 or 2. Respond with number only not any words.***
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system,
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=False)
        response = agent_executor.invoke({"input": query})["output"]
        return response


