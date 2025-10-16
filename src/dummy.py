import os

from datapizza.agents import Agent
from datapizza.clients.google import GoogleClient
from datapizza.clients.openai_like import OpenAILikeClient
from datapizza.tools import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def dummy(x: str) -> str:
    return "ok:" + x


# client = OpenAILikeClient(api_key="", model="llama3.2:1b", base_url="http://localhost:11434/v1")
client = GoogleClient(api_key=os.getenv("GOOGLE_API_KEY"))
agent = Agent(name="t", client=client, tools=[dummy], system_prompt="test")

try:
    res = agent.run("call dummy with 'hello'")
    print("OK:", res.text)
except Exception as e:
    print("MODEL ERROR:", e)
