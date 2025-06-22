from enum import Enum

class SentenceType(Enum):
    DECLARATIVE = "Declarative"
    IMPERATIVE = "Imperative"
    INTERROGATIVE = "Interrogative"
    EXCLAMATORY = "Exclamatory"
    UNDEFINED = "Undefined"

class SemanticBlock:
    def __init__(self, 
        block, 
        context, 
        last_change, 
        location:(int, int),
        sentence_type:SentenceType = SentenceType.UNDEFINED, 
        ):
        self.block = block
        self.context = context
        self.last_change = last_change
        self.location = location
        self.sentence_type = sentence_type
        

