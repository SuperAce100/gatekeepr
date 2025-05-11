from ast import List
import os
import asyncio
from agents import Agent, Runner
from rich.console import Console
from rich.rule import Rule

from create_sub_agents import create_sub_agents
from prompts import orchestrator_system_prompt
console = Console()

import agentops
from dotenv import load_dotenv

load_dotenv()

agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

async def main():

    input_dir = ".data/svgrl"
    sub_agents: List[Agent] = create_sub_agents(input_dir)

    console.print(f"Created {len(sub_agents)} sub-agents:", style="bold green")
    for sub_agent in sub_agents:
        console.print(Rule(style="bold green", title=sub_agent.name, align="left"))
        console.print(sub_agent.handoff_description, style="dim")


    orchestrator = Agent(
        name="Orchestrator",
        instructions=orchestrator_system_prompt,
        handoff_description="The orchestrator, who should be updated after all changes have been made.",
        tools=[sub_agent.as_tool(sub_agent.name.replace(' ', '_').replace('.', '_').replace('/', '_')[:50], sub_agent.handoff_description) for sub_agent in sub_agents],
        model="gpt-4.1-mini"
    )

    

    # print(orchestrator.handoffs)

    result = await Runner.run(orchestrator, "Add dark mode to the viewers")

    console.print(result.final_output, style="bold")
if __name__ == "__main__":
    asyncio.run(main())






