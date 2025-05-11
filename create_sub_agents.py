import os
import random
from llms import llm_call
from prompts import file_reader_system_prompt
import fnmatch

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
            print(f"Error reading .gitignore: {str(e)}")
    
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



# def create_sub_agents(input_dir):
#     files = list_files(input_dir)

#     for file in files:
#         print(file)

# create_sub_agents("data")

if __name__ == "__main__":
    input_dir = ".data/autolibra"
    files = list_files(input_dir)
    for file in files:
        print(file[1][:100])
    print(len(files))

    random_files = random.sample(files, 10)
    import concurrent.futures
    
    summaries = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(summarize_file, file): file for file in random_files}
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            summaries[file[0]] = future.result()
    
    # Print results sequentially
    for file in random_files:
        print("="*100)
        print(file[0])
        print(file[1][:100])
        print("-"*100)
        print(summaries[file[0]])
    
