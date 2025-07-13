from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def start(self):
        """
        This method is called when the agent starts.
        Subclasses must implement this method.
        """
        pass

    @abstractmethod
    def update(self):
        """
        This method is called to update the agent's state.
        Subclasses must implement this method.
        """
        pass