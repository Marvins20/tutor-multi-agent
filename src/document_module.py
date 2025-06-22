from semantic_block import SemanticBlock, SentenceType

class DocumentModule:
    def __init__(self, comparator, file_parser, file_manager):
        super().__init__()
        self.comparator = comparator
        self.file_parser = file_parser
        self.file_manager = file_manager
        self.file_index = {}

    def read_file_content(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read(),

    def check_file_last_change(self, file_path) -> SemanticBlock:
        content = (self.read_file_content(file_path))[0]
        ast = self.file_parser.parse(content)

        if file_path not in self.file_index:
            self.file_index[file_path] = (content,ast)

            return SemanticBlock(
                block=content,
                context=content,
                last_change=content,
                sentence_type=SentenceType.UNDEFINED,
                location=(0, len(content.split('\n')))
            )
        

        changes = self.comparator.compare_file_content(self.file_index[file_path][0] ,content )
        sig_changes = self.block_significative_changes(changes)

        if sig_changes:
            block = self.file_manager.get_block_at_line(sig_changes[0][0], ast)
            context = self.file_manager.get_context_at_line(sig_changes[0][0], ast)
            last_change =sig_changes[1]
            sentence_type=sentence_type=SentenceType.UNDEFINED,
            location = sig_changes[0]

            return SemanticBlock(
                block, context, last_change, location, sentence_type
            )
        return None
    
    def answer_in_document(self, file_path, block: SemanticBlock):
        if not file_path in self.file_index:
            return 
        
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

        # if block.location[0] < 1 or block.location[1] > len(lines):
        #     raise ValueError(f"Line number {block.location[0]} is out of range for the file.")

        text = self.file_manager.rewrite_block_at_line(block.location[0], block.block, self.file_index[file_path][1])
        lines = text.split("\n")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)   

    def block_significative_changes(self, changes):
        filtered_changes = [change for change in changes if change[1].strip() != "" ]
        if not filtered_changes:
            return None
        
        visit_values = [change[0] for change in filtered_changes]
        min_visit = min(visit_values)
        max_visit = max(visit_values)
        
        full_changes = '\n'.join(change[1] for change in changes)

        return ((min_visit, max_visit), full_changes)        



        
    

    

