from typing_extensions import override
from agent import Agent
import os


class ProfessorAgent(Agent):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.messages = []

    def start(self, ):

    def update(self):\
        
        if len(messages) > 0:
            message = self.messages.pop(0)
            process(message)
        
        pass