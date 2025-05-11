from email import utils
import os
import random
from llms import llm_call
from prompts import file_reader_system_prompt, sub_agent_system_prompt
import fnmatch
import concurrent.futures
from agents import Agent, function_tool
from rich.progress import track
from rich.console import Console
from rich.rule import Rule

console = Console()


def list_files(input_dir):
    result = []
    gitignore_patterns = []
    
    # Check if .gitignore exists and read patterns
    gitignore_path = os.path.join(input_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            console.print(f"Error reading .gitignore: {str(e)}", style="bold red")
    
    for root, dirs, files in os.walk(input_dir):
        # Filter out directories that start with '.'
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # Apply gitignore patterns to directories
        if gitignore_patterns:
            dirs_to_keep = []
            for d in dirs:
                rel_dir = os.path.relpath(os.path.join(root, d), input_dir)
                should_ignore = False
                for pattern in gitignore_patterns:
                    if fnmatch.fnmatch(rel_dir, pattern) or fnmatch.fnmatch(f"{rel_dir}/", pattern):
                        should_ignore = True
                        break
                if not should_ignore:
                    dirs_to_keep.append(d)
            dirs[:] = dirs_to_keep
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, input_dir)
            
            # Skip files that match gitignore patterns
            if gitignore_patterns and any(fnmatch.fnmatch(rel_path, pattern) for pattern in gitignore_patterns):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result.append((rel_path, content))
            except Exception as e:
                result.append((rel_path, f"Error reading file: {str(e)}"))
    return result

def summarize_file(file):
    prompt = f"Summarize the contents of the file {file}."
    system_prompt = file_reader_system_prompt
    return llm_call(prompt, system_prompt)

INPUT_DIR = ""


@function_tool
def update_file(file_name: str, old_content: str, new_content: str):
    global INPUT_DIR

    file_path = os.path.join(INPUT_DIR, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        old_file_content = f.read()
        new_file_content = utils.find_and_replace(old_content, new_content, old_file_content)
        f.write(new_file_content)

    console.print(f"Updating {file_name} with diff: >>>>>>[red]{old_content}[/red]\n=======\nz[green]{new_content}[/green]\n<<<<<<", style="dim")
    return f"Update successful!"

def create_sub_agents(input_dir):
    global INPUT_DIR
    INPUT_DIR = input_dir
    files = list_files(input_dir)

    def create_sub_agent(file):
        summary = summarize_file(file)
        agent = Agent(
            name=file[0], handoff_description=summary, instructions=sub_agent_system_prompt.format(file_name=file[0], file_content=file[1]), tools=[update_file], model="gpt-4.1-mini")
        return agent

    
    sub_agents = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(create_sub_agent, file) for file in files]
        for future in track(concurrent.futures.as_completed(futures), total=len(futures), description="Creating sub-agents"):
            file = next(file for file, fut in zip(files, futures) if fut == future)
            try:
                sub_agent = future.result()
                sub_agents.append(sub_agent)
            except Exception as e:
                console.print(f"Error creating agent for {file[0]}: {str(e)}", style="bold red")
    return sub_agents



if __name__ == "__main__":
    input_dir = ".data/autolibra"

    sub_agents = create_sub_agents(input_dir)
    console.print(f"Created {len(sub_agents)} sub-agents:", style="bold green")
    for sub_agent in sub_agents:
        console.print(Rule(style="bold green", title=sub_agent.name, align="left"))
        console.print(sub_agent.handoff_description, style="dim")

