
import difflib
class Comparator():
    def __init__(self):
        super().__init__()
        self.file_contents = {}

    def compare_file_content(self, fst_content, snd_content):
        diff = self.get_diff(fst_content, snd_content)

        added_lines = []
        new_line_number = 1 

        for line in diff:
            if line.startswith('+ '):
                # Unescape the characters in the added line
                unescaped_line = line[2:].replace('\\+', '+').replace('\\-', '-')
                added_lines.append((new_line_number, unescaped_line))
                new_line_number += 1
            elif line.startswith('  '):
                new_line_number += 1

        return added_lines

    def get_diff(self, old_content:str, new_content:str):
        old_lines = [line.replace('+', '\\+').replace('-', '\\-') for line in old_content.split('\n')]
        new_lines = [line.replace('+', '\\+').replace('-', '\\-') for line in new_content.split('\n')]

        d = difflib.Differ()
        diff = list(d.compare(old_lines, new_lines))
        return diff
        
        # changes = '\n'.join(line[2:] for line in diff if line.startswith('+ '))
        # changes = '\n'.join(line for line in diff)
        
    
    # def append_in_context(file_path, location, message):
    #     content = self.read_file_content(file_path)
    #     # Find the closest matching location in the content
    #     best_match = None
    #     best_ratio = 0
        
    #     # Split content into paragraphs and compare each
    #     paragraphs = new_content.split('\n\n')
    #     for paragraph in paragraphs:
    #         ratio = difflib.SequenceMatcher(None, location, paragraph).ratio()
    #         if ratio > best_ratio:
    #             best_ratio = ratio
    #             best_match = paragraph
        
    #     # If no good match found, return without changes
    #     if best_ratio < 0.5:  # Threshold for minimum similarity
    #         return new_content
            
    #     # Insert message after the matched paragraph
    #     old_content = new_content
    #     new_content = new_content.replace(best_match, best_match + '\n' + message)    

    #     return

            

    