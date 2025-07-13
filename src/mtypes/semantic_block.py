from dataclasses import dataclass
from enum import Enum

class SentenceType(Enum):
    DECLARATIVE = "Declarative"
    IMPERATIVE = "Imperative"
    INTERROGATIVE = "Interrogative"
    EVALUATIVE = "Exclamatory"
    ANSWER = "Answer"
    FINISHED = "Finished"
    UNDEFINED = "Undefined"

@dataclass
class SemanticBlock:
    change_class: str
    origin_file_path: str
    content: str
    last_change: str
    block: str
    location: tuple[int, int]
    context: str
    sentence_type: SentenceType

        

