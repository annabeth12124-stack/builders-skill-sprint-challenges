"""
Challenge 4: The Full Agent — Tools + Memory + Streaming
Combine everything into one powerful agent.
Model: Amazon Nova Pro via Bedrock

Instructions:
  1. Fill in ALL the TODO sections
  2. Run: python starter.py
  3. Have a full conversation using all tools!
"""

import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"

from datetime import date, datetime

MODEL = "us.amazon.nova-pro-v1:0"


# ============================================================
# TODO 1: Import everything you need
# ============================================================
# Hint: You need Agent, tool from strands
#       calculator, mem0_memory from strands_tools

# Your imports here
import requests
from strands import Agent, tool
from strands_tools import calculator, mem0_memory


# ============================================================
# TODO 2: Create a streaming callback handler
# ============================================================
# This function gets called for every chunk of text the agent generates
# Hint:
# def stream_callback(**kwargs):
#     if "data" in kwargs:
#         print(kwargs["data"], end="", flush=True)
#     elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
#         print(f"\n🔧 Using tool: {kwargs['current_tool_use']['name']}")

# Your callback here


# ============================================================
# TODO 3: Create custom tools — weather and age_calculator
# ============================================================
# Reuse your code from Challenge 2!

# Your tools here
@tool
def weather(city: str) -> str:
    """Get the current weather for a city.
    Args:
        city: The name of the city.
    """
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        return r.text
    except:
        return f"Weather in {city}: Sunny, 30°C"

@tool
def age_calculator(birth_date: str) -> str:
    """Calculate age from a birth date.
    Args:
        birth_date: Date of birth in YYYY-MM-DD format.
    """
    today = date.today()
    born = datetime.strptime(birth_date, "%Y-%m-%d").date()
    age = today.year - born.year - (
        (today.month, today.day) < (born.month, born.day)
    )
    return f"Someone born on {birth_date} is {age} years old."


# ============================================================
# TODO 4: Create the full agent with ALL tools + memory + streaming
# ============================================================
# Hint: Agent(
#     model=MODEL,
#     tools=[calculator, weather, age_calculator, mem0_memory],
#     callback_handler=stream_callback,
#     system_prompt="..."
# )

def stream_handler(**kwargs):
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)

    elif (
        "current_tool_use" in kwargs
        and kwargs["current_tool_use"].get("name")
    ):
        print(
            f"\n🔧 Using tool: {kwargs['current_tool_use']['name']}"
        )


agent = Agent(
    model=MODEL,
    tools=[calculator, weather, age_calculator, mem0_memory],
    callback_handler=stream_handler,
    system_prompt="""You are a fun, helpful assistant! 🤖
You have access to: calculator, weather, age_calculator, and memory tools.
- Use calculator for any math
- Use weather to check any city's weather  
- Use age_calculator for birth dates
- Use mem0_memory to remember and recall user info
Be friendly and use emojis!"""
)


# ============================================================
# TODO 5: Interactive chat loop
# ============================================================

print("🤖 Full Agent Ready! Type 'quit' to exit.")
print("Try: 'What's the weather in Delhi and how old is someone born 2000-01-01?'")
print("Try: 'Remember my name is [name]' then 'What's my name?'\n")

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye! 👋")
            break

        print("\nAgent: ", end="")
        # TODO: Call the agent with user_input
        agent(user_input)
        print("\n")

    except KeyboardInterrupt:
        print("\nBye! 👋")
        break

print("\n✅ Challenge 4 complete! 🏆")
