class Dockerfile:
    
    def __init__(self, filepath="Dockerfile"):
        self.filepath = filepath
        with open(filepath, "w") as f:
            f.write("")
    
    def write_line(self, text):
        with open(self.filepath, "a") as f:
            f.write(text.rstrip("\n") + "\n")
            
    def run(self, text):
        self.write_line("RUN " + text)
    
    def run_together(self, commands):
        self.run(" \\\n &&  ".join(commands))
        
    def run_separately(self, commands):
        self.run("; ".join(commands))