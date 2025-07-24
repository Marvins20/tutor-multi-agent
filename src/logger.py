import os
from utils.token_counter import count_tokens


class Logger:
    # TODO turn into abstract classes
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.group =""

    def __new__(cls, id):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def set_group(self, group):
        self.group = group
        print("------------logger-----------",group)
        return self.group

    #HAve to found a way 
    def log_token_and_time_usage(self, content, no_prompt, time):
        log_dir = ".log"
        os.makedirs(log_dir, exist_ok=True)
        tkn_quantity = count_tokens(content)
        tkn_no_quantity = count_tokens(no_prompt)
        file_path = os.path.join(log_dir, f"tokens_{self.id}.log")
        with open(file_path, "a") as log_file:
            log_file.write(f"{self.group}:{tkn_quantity},{tkn_no_quantity};{time}\n")
