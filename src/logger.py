import os
from utils.token_counter import count_tokens

class Logger:
    # TODO turn into abstract classes
    def __init__(self):
        super().__init__()

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def set_id(self, id):
        self.id = id

    def set_group(self, group):
        self.group = group
        return self.group

    #HAve to found a way 
    def log_token_and_time_usage(self, content, no_prompt, time):
        if not self.id or not self.group:
            print(f"Id ou grupo não definidos; id: {self.id}; grupo: {self.group}")
        log_dir = ".log"
        os.makedirs(log_dir, exist_ok=True)

        tkn_quantity = count_tokens(content)
        tkn_no_quantity = count_tokens(no_prompt)

        
        file_path = os.path.join(log_dir, f"tokens_{self.id}.log")

        # Create file with header if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, "w") as log_file:
                log_file.write("steps,tokens,tokens_no_prompt,time\n")

        with open(file_path, "a") as log_file:
            log_file.write(f"{self.group},{tkn_quantity},{tkn_no_quantity},{time}\n")

        return tkn_quantity