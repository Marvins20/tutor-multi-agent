
import difflib

# TODO preciso fazer um indíce do arquivo em que ele pode ser dividido em blocos
# semânticos, com um indíce de localidade e quais partes


class FileChangeDetector():
    def __init__(self):
        super().__init__()
        self.file_contents = {}
    def read_file_content(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read(),

    def extract_file_index(file_content):
        

    def compare_file_content(self, file_path):
        if file_path in self.file_contents:
            old_content = self.file_contents[file_path]
            new_content = self.read_file_content(file_path)
            if old_content != new_content:
                self.file_contents[file_path] = new_content
                return self.get_diff(old_content, new_content)
            return ""
        
        self.file_contents[file_path] = self.read_file_content(file_path)
        return self.file_contents[file_path]
    
    def append_in_context(file_path, location, message):
        content = self.read_file_content(file_path)
        # Find the closest matching location in the content
        best_match = None
        best_ratio = 0
        
        # Split content into paragraphs and compare each
        paragraphs = new_content.split('\n\n')
        for paragraph in paragraphs:
            ratio = difflib.SequenceMatcher(None, location, paragraph).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = paragraph
        
        # If no good match found, return without changes
        if best_ratio < 0.5:  # Threshold for minimum similarity
            return new_content
            
        # Insert message after the matched paragraph
        old_content = new_content
        new_content = new_content.replace(best_match, best_match + '\n' + message)    

        return

            

    def get_diff(self, old_content, new_content):
        d = difflib.Differ()
        d = difflib.Differ()
        diff = list(d.compare(old_content.split('\n\n'), new_content.split('\n\n') ))
        changes = '\n'.join(line[2:] for line in diff if line.startswith('+ '))
        return changes