from dataclasses import dataclass
from typing import Type
from enum import Enum

from mtypes.document_change import DocumentChange
from mtypes.semantic_block import SemanticBlock, SentenceType

class CallType(Enum):
    ANSWER = "Answer"
    RESEARCH = "Research"
    NEXT_STEP = "Next Step"
    EVALUATIVE = "Evaluative"
    PROFILE = "Profile"
    ELABORATE_QUESTION = "Elaborate Question"
    DECLARATIVE = "Declarative"

@dataclass
class TextRange:
    start: int
    end: int

@dataclass
class FileLocation:
    file_path: str
    line_number: int
    text_range: TextRange


@dataclass
class ContextedCall:
    topic: str
    start_time: int
    wait_time: int
    block_context: str
    full_context: str
    type: CallType
    source: FileLocation
    target: FileLocation
    
    @classmethod
    def from_interaction(cls: Type['ContextedCall'], 
        interaction: SemanticBlock,
        topic=None,
        block_context=None,
        full_context=None,
        source=None,
        target=None) -> 'ContextedCall':

        def call_type_from_sentece_type(sentence_type: SentenceType):
            if sentence_type == SentenceType.IMPERATIVE:
                return CallType.ANSWER
            elif sentence_type == SentenceType.INTERROGATIVE:
                return CallType.ANSWER
            elif sentence_type == SentenceType.FINISHED:
                return CallType.NEXT_STEP
            else:
                return CallType.DECLARATIVE

        topic = topic if topic else interaction.content
        block_context = block_context if block_context else interaction.block
        full_context = full_context if full_context else interaction.context
        source = source if source else FileLocation(interaction.origin_file_path, 
            FileLocation(interaction.location[1],
                interaction.location[1][0],
                interaction.location[1][1]))
        target =  target if target else target

        if interaction.sentence_type == SentenceType.IMPERATIVE:
            topic=interaction.block
            target=FileLocation(interaction.origin_file_path, 
                FileLocation(interaction.location[0],
                    interaction.location[0][0],
                    interaction.location[0][1]))
        elif interaction.sentence_type == SentenceType.INTERROGATIVE:
            topic = interaction.last_change,

        elif interaction.sentence_type == SentenceType.FINISHED:
            topic=topic,
            block_context = block_context
            full_context = full_context

        return cls(
            topic=topic,
            start_time=0,
            wait_time=0,
            block_context=block_context,
            full_context=full_context,
            type=call_type_from_sentece_type(interaction.sentence_type),
            source=source,
            target=target,   
        ) 