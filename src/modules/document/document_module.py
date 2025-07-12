from ast import Tuple
from dataclasses import dataclass
import os
from contextlib import ExitStack
from comparator import Comparator, TextChange
from md_parser import MarkdownParser 
from md_manager import MarkdownManager
from typing import List, Tuple 

@dataclass
class DocumentChange:
    file_path: str
    line_number: int
    content: str
    modified_text: List[TextChange]
    affeted_subtypes: List[str]
    block: Tuple(str, str)
    context: str
    

class DocumentModule:
    # TODO turn into abstract classes
    def __init__(self, comparator: Comparator, file_parser: MarkdownParser, file_manager: MarkdownManager):
        super().__init__()
        self.comparator = comparator
        self.file_parser = file_parser
        self.file_manager = file_manager
        self.file_index = {}

    def start(self, directory_path):
        with ExitStack() as stack:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        file = stack.enter_context(open(file_path, 'r', encoding='utf-8'))
                        content = file.read()
                        ast = self.parse_text(content)
                        self.file_index[file_path] = (content, ast)
                        print(f"Indexed file: {file_path}")
        total_bytes = 0
        for file_path, (content, ast) in self.file_index.items():
            file_bytes = len(content.encode('utf-8'))
            total_bytes += file_bytes
            print(f"File: {file_path}, Content Length: {len(content)} characters, Size: {file_bytes} bytes")

        print(f"\nTotal memory usage: {total_bytes} bytes ({total_bytes / 1024:.2f} KB, {total_bytes / (1024*1024):.2f} MB)")

    def read_file_content(self, file_path):
        with ExitStack() as stack:
            file = stack.enter_context(open(file_path, 'r', encoding='utf-8'))
            content = file.read()
            ast = self.parse_text(content)
            return (content, ast)


    def parse_text(self, text):
        return self.file_parser.parse(text)

    def __init__(self, comparator, file_parser, file_manager):
        self.comparator = comparator
        self.file_parser = file_parser
        self.file_manager = file_manager
        self.file_index = {}

    def check_file_last_change(self, file_path:str) -> List[DocumentChange]:
        (content, ast) = self.read_file_content(file_path)
        print(f"Indexed file: {file_path}")

        if file_path not in self.file_index:
            self.file_index[file_path] = (content,ast)
            return []

        modified_lines = self.comparator.compare_file_content(self.file_index[file_path][0] ,content )
        self.file_index[file_path] = (content,ast)

        changes = []
        for line in modified_lines:
            block = self.file_manager.get_block_at_line(line.line_number, ast)
            context = content
            affected_subtypes = self.extract_modified_subtypes(line.text_changes, line.line_number, ast)
            change  = DocumentChange(
                file_path=file_path,
                line_number=line.line_number,
                content=line.content,
                modified_text=line.text_changes,
                affected_subtypes=affected_subtypes,
                block=block,
                context=context
            )
            changes.append(change)
        
        return changes

    

    def extract_modified_subtypes(self, text_changes, line_number, ast):
        def ranges_intersect(range1, range2):
            return not (range1[1] < range2[0] or range1[0] > range2[1])

        (_, text_type_ranges) = self.file_manager.get_text_at_line(line_number, ast)

        intersecting_types = []
        for (text, text_range) in text_changes:
            for (text_type, type_range) in text_type_ranges:
                if ranges_intersect(text_range, type_range):
                    intersecting_types.append((text_type, type_range))
                    break  # No need to check further if an intersection is found
        return intersecting_types



    def answer_in_document(self, file_path, block):
        if not file_path in self.file_index:
            return 
        
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

# TEST BLOCK

# dm = DocumentModule(Comparator(),MarkdownParser(), MarkdownManager())
# folder_to_monitor = "/Users/marcusabr/Documents/AI Journey"
# dm.start(folder_to_monitor)



       



        
    

    

