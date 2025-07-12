from typing_extensions import override
from agent import Agent
import os

class DirectorAgent(Agent):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.messages = []

    def start(self, ):
        goal_file = os.path.join(self.path, "GOAL.md")
        if os.path.exists(goal_file):
            print(f"Found GOAL.md at {goal_file}")
        else:
            with open(goal_file, 'w') as f:
                f.write("# Project Goal\n\nPlease define your project goal here.\n")
            print(f"Created GOAL.md at {goal_file}")            
            print(f"GOAL.md not found in {self.path}")

    def update(self):\
        
        if len(messages) > 0:
            message = self.messages.pop(0)
            process(message)

        # TODO check context stack
        
        pass