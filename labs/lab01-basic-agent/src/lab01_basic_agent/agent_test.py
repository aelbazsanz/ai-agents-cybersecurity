# imports
from lab01_basic_agent.agent import Agent

# Create an instance of the Agent class and run it with a sample user input.
agent = Agent()

from lab01_basic_agent.agent import Agent

agent = Agent()

result = agent.run(
    "Use the available tools to determine how many days remain until "
    "October 1, 2026. First obtain today's UTC date, then use that "
    "result to calculate the number of days."
)

print("\nFinal answer:")
print(result)