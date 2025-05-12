import chainlit as cl

#dummy function to create sub-agents
@cl.step(type="create_sub_agents")
async def create_sub_agents():
    await cl.sleep(1)
    sub_agents = [
        {
            "name": "Code Assistant",
            "handoff_description": "Helps with writing, debugging, and explaining code across various programming languages."
        },
        {
            "name": "Data Analyst",
            "handoff_description": "Specializes in data processing, visualization, and statistical analysis."
        },
        {
            "name": "DevOps Helper",
            "handoff_description": "Assists with deployment, CI/CD pipelines, and infrastructure management."
        }
    ]   

    return sub_agents

@cl.step(type="handoff_to_orchestrator")
async def handoff_to_orchestrator(message):
    await cl.sleep(1)
    # Simulate file changes from different sub-agents
    file_changes = [
        {
            "agent": "Code Assistant",
            "filename": "main.py",
            "old_text": "def process_data(data):\n    # TODO: Implement data processing\n    return data",
            "new_text": "def process_data(data):\n    # Clean missing values\n    data = data.dropna()\n    \n    # Normalize numeric columns\n    numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns\n    data[numeric_cols] = (data[numeric_cols] - data[numeric_cols].mean()) / data[numeric_cols].std()\n    \n    return data"
        },
        {
            "agent": "Data Analyst",
            "filename": "visualization.py",
            "old_text": "import matplotlib.pyplot as plt\n\ndef plot_data(data):\n    # TODO: Implement visualization\n    pass",
            "new_text": "import matplotlib.pyplot as plt\nimport seaborn as sns\n\ndef plot_data(data):\n    # Set style\n    sns.set_theme(style='whitegrid')\n    \n    # Create figure with subplots\n    fig, axes = plt.subplots(2, 2, figsize=(12, 10))\n    \n    # Plot distributions\n    for i, col in enumerate(data.select_dtypes('number').columns[:4]):\n        ax = axes[i//2, i%2]\n        sns.histplot(data[col], ax=ax, kde=True)\n        ax.set_title(f'Distribution of {col}')\n    \n    return fig"
        },
        {
            "agent": "DevOps Helper",
            "filename": "Dockerfile",
            "old_text": "FROM python:3.9-slim\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\n\nCOPY . .\n\nCMD [\"python\", \"app.py\"]",
            "new_text": "FROM python:3.9-slim\nWORKDIR /usr/src/app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nEXPOSE 8000\n\nCMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"app:app\"]"
        }
    ]
    
    # Create a response message
    response_content = f"I've analyzed your message: '{message}' and assigned tasks to the following sub-agents:"
    
    # Create CodeDiffViewer elements for each file change
    elements = []
    for change in file_changes:
        response_content += f"\n\n**{change['agent']}** has modified `{change['filename']}`"
        
        # Pass the diff object with the correct structure expected by CodeDiffViewer
        elements.append(cl.CustomElement(
            name="CodeDiffViewer", 
            props={
                "filename": change["filename"],
                "old_text": change["old_text"],
                "new_text": change["new_text"]
            }
        ))
    
    return {"content": response_content, "elements": elements}

@cl.on_message
async def on_message(message: cl.Message):
    # Then, hand off the message to the orchestrator
    response = await handoff_to_orchestrator(message.content)
    
    # Send the orchestrator's response back to the user
    await cl.Message(
        content=response["content"],
        elements=response["elements"]
    ).send()

@cl.on_chat_start
async def on_chat_start():
    sub_agents = await create_sub_agents()

    sub_agent_element = cl.CustomElement(
        name="Sub-Agent",
        props={"agents": sub_agents}
    )
    
    await cl.Message(
        content="Creating sub-agents...",
        elements=[sub_agent_element]
    ).send()

if __name__ == "__main__":
    print("Running...")
