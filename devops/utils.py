"""
Not using mistletoe because:
TypeError: <mistletoe.block_token.TableRow object at 0x7f92383229e8> is not JSON serializable
"""
def get_first_column(filepath):
    with open(filepath) as f:
        values = []
        for line in f:
            if line.count("|") >= 2 and line.count("--") == 0:
                values.append(line.split("|")[1].strip())
                
    # removing column header
    values = values[1:]
    
    return values
    
def get_python_requirements(filepath):
    with open(filepath) as f:
        return f.read().split("\n")
        
def get_reqs(filepath):
    if filepath.endswith("requirements.txt"):
        return get_python_requirements(filepath)
    elif filepath.endswith(".md"):
        return get_first_column(filepath)