from google.adk.agents import Agent

from multi_tool_agent import prompt

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="コンシェルジュ",
    instruction=prompt.ROOT_AGENT_INSTR,
)
