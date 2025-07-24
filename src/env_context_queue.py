from typing import List, Optional, Tuple
import json
from document_module.document_module import DocumentChange
from mtypes.semantic_block import SemanticBlock, SentenceType
import queue


class EnvironmentContextQueue:
    def __init__(self):
        self.interaction_queue: List[SemanticBlock] = []
        self.answer_queue = []

    def is_empty(self) -> bool:
        return len(self.interaction_queue) == 0

    def push_interactions(self, interactions: List[DocumentChange]):
        for interaction in interactions:
            question_blocks = self.extract_questions(interaction)
            interaction_block = self.extract_block_with_type(interaction)

            for question in question_blocks:
                self.interaction_queue.append(question)
            self.interaction_queue.append(interaction_block) 
            self.write_context_queue()
        

    def write_context_queue(self):
        queue_data = []
        for interaction in self.interaction_queue:
            interaction_data = {
                "content": interaction.content,
                "block": interaction.block,
                "change_class": interaction.change_class,
                "origin_file_path": interaction.origin_file_path,
                "sentence_type": interaction.sentence_type.value,
                "context": interaction.context,
                "location": interaction.location,
                "last_change": interaction.last_change
            }
            
            queue_data.append(interaction_data)
        
        with open("semantic_blocks.json", 'w', encoding='utf-8') as output_file:
            json.dump(queue_data, output_file, indent=4, ensure_ascii=False)

    def pop_interaction(self) -> Optional[SemanticBlock]:
        self.refine_interaction_queue()
        return self.interaction_queue.pop(0) if self.interaction_queue else None

    def extract_block_with_type(self, interaction:DocumentChange):
        last_change = self.block_line_changes(interaction.line_number,interaction.modified_text)

        sentence_type = None

        if interaction.block[1] == "block_highlight":
            sentence_type = SentenceType.IMPERATIVE

        elif "block_keyword" == interaction.block[1] and interaction.block[0].strip().startswith("#EVAL"):
            sentence_type = SentenceType.EVALUATIVE

        elif "block_keyword" == interaction.block[1] and interaction.block[0].strip().startswith("#QST"):
            sentence_type = SentenceType.ANSWER

        elif "block_keyword" in interaction.block[1] and interaction.block[0].strip().startswith("#NXT"):
            sentence_type = SentenceType.FINISHED
        else:
            sentence_type = SentenceType.DECLARATIVE

        return SemanticBlock(
                content=interaction.content,
                block=interaction.block,
                change_class=(interaction.class_name+"-"+str(interaction.line_number)),
                origin_file_path=interaction.file_path,
                sentence_type=sentence_type,
                context=interaction.context,
                location=last_change[1],
                last_change=last_change[0]
            )

    def refine_interaction_queue(self):
        pass

    def block_line_changes(self, line_number:int, changes: List[Tuple[str, Tuple[int, int]]]):

        if not changes:
            return ("", (line_number, (0, 0)))
       
        range_starts = [change[1][0] for change in changes]
        range_ends = [change[1][1] for change in changes]
        min_range = min(range_starts)
        max_range = max(range_ends)
        
        full_changes = '\n'.join(change[0] for change in changes)

        return (full_changes, (line_number, (min_range, max_range))) 

    def extract_questions(self, interaction: DocumentChange):
        question_subtypes = [subtype for subtype in interaction.affected_subtypes if subtype[0] == "question"]
        seen_ranges = set()
        result_questions = []
        for question in question_subtypes:
            if question[1] not in seen_ranges:
                result_questions.append(question)
                seen_ranges.add(question[1]) 

        result_blocks = []   
        for  question in result_questions:
            block = SemanticBlock(
                content=interaction.content,
                block=interaction.block,
                change_class=(interaction.class_name+"-"+str(interaction.line_number)),
                origin_file_path=interaction.file_path,
                sentence_type=SentenceType.INTERROGATIVE,
                context=interaction.context,
                location=(interaction.line_number,(question[1])),
                last_change=interaction.content[question[1][0]:question[1][1]]
            )
            result_blocks.append(block)

        return result_blocks
