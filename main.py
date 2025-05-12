import chainlit as cl
from create_sub_agents import create_sub_agents
from orchestrator import run_orchestrator


sub_agents = []

@cl.on_message
async def on_message(message: cl.Message):
    global sub_agents

    response = await run_orchestrator(message.content, sub_agents)
    
    await cl.Message(
        content=f"Done! {response.final_output}"
    ).send()

@cl.on_chat_start
async def on_chat_start():
    global sub_agents
    input_dir = ".data/portfolio/asanshay-portfolio"
    with cl.Step(name="create sub-agents"):
        sub_agents = await create_sub_agents(input_dir)

    sub_agent_element = cl.CustomElement(
        name="Sub-Agent",
        props={"agents": [{"name": sub_agent.name, "description": sub_agent.handoff_description} for sub_agent in sub_agents]}
    )
    
    await cl.Message(
        content=f"## Created {len(sub_agents)} sub-agents:",
        elements=[sub_agent_element]
    ).send()

if __name__ == "__main__":
    print("Running...")
