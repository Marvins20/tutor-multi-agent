from dataclasses import dataclass
from enum import Enum
from hashlib import algorithms_available

class SentenceType(Enum):
    DECLARATIVE = "Declarative"
    IMPERATIVE = "Imperative"
    INTERROGATIVE = "Interrogative"
    EVALUATIVE = "Exclamatory"
    ANSWER = "Answer"
    UNDEFINED = "Undefined"

@dataclass
class SemanticBlock:
    origin_file_path: str
    last_change: str
    block: str
    location: tuple[int, int]
    context: str
    sentence_type: SentenceType

        

