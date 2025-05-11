import os

def list_files(input_dir):
    result = []
    for root, dirs, files in os.walk(input_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)
                rel_path = os.path.relpath(file_path, input_dir)
                result.append((rel_path, content))
            except Exception as e:
                rel_path = os.path.relpath(file_path, input_dir)
                result.append((rel_path, f"Error reading file: {str(e)}"))
    return result

# def create_sub_agents(input_dir):
#     files = list_files(input_dir)

#     for file in files:
#         print(file)

# create_sub_agents("data")

if __name__ == "__main__":
    input_dir = ".data/autolibra"
    files = list_files(input_dir)
    for file in files:
        print(file)
    print(len(files))

