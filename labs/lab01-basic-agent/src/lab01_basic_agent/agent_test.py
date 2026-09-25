# imports
from lab01_basic_agent.agent import Agent

# Create an instance of the Agent class and run it with a sample user input.
agent = Agent()

result = agent.run("What time is it right now?")

print("\nFinal answer:")
print(result)