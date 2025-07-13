
from dataclasses import dataclass
from typing import List, Tuple
import difflib
from typing_extensions import TypeAlias

Location: TypeAlias = Tuple[int, int]

@dataclass
class TextChange:
    text: str
    location: Location

@dataclass
class LineChange:
    line_number: int
    content: str
    text_changes: List[TextChange]


class Comparator():
    def __init__(self):
        super().__init__()
        self.file_contents = {}

    def compare_file_content(self, fst_content: str, snd_content: str) ->List[LineChange]:
        diff_between_content = self.get_diff(fst_content, snd_content)
        changes = self.filter_changes(diff_between_content)
        return changes

    def get_diff(self, old_content: str, new_content: str) -> List[str]:
        old_lines = [line.replace('+', '\\+').replace('-', '\\-').replace('?', '\\?') for line in old_content.split('\n')]
        new_lines = [line.replace('+', '\\+').replace('-', '\\-').replace('?', '\\?') for line in new_content.split('\n')]

        d = difflib.Differ()
        diff = list(d.compare(old_lines, new_lines))

        diff = [line.replace('\\+', '+', ).replace('\\-', '-').replace('\\?', '?') for line in diff]
        return diff
        
    
    def filter_changes(self, diff: List[str]) -> List[LineChange]:
        modified_lines: List[str] = []
        result_lines: List[LineChange] = []
        new_line_number = 1
        
        for line in diff:
            if line.startswith('+ '):
                unescaped_line = line[2:]
                if len(modified_lines) > 0 and modified_lines[-1].startswith('- '):
                    char_diff = self.get_char_diff(modified_lines[-1][2:], unescaped_line)
                    result_lines.append(LineChange(new_line_number, unescaped_line, char_diff))
                    print(new_line_number, unescaped_line)
                else: 
                    result_lines.append(LineChange(new_line_number, unescaped_line, []))
                    print(new_line_number, unescaped_line)
                new_line_number += 1
            elif line.startswith('  '):                
                new_line_number += 1

            modified_lines.append(line)

        return result_lines

    def get_char_diff(self, old_line: str, new_line: str) -> List[TextChange]:
        d = difflib.Differ()
        diff = list(d.compare(old_line, new_line))
        char_diff: List[Tuple[str, int]] = []

        for i, char in enumerate(diff):
            if char.startswith('+ '):
                char_diff.append((char[2:], i))

        return self.group_char_diff(char_diff)

    def group_char_diff(self, char_diff: List[Tuple[str, int]]) -> List[TextChange]:
        groups = []

        for (char, idx) in char_diff:
            if not groups or idx != groups[-1][1][1] + 1:
                groups.append((char, (idx, idx)))
            else:
                (last_c, (start,end)) = groups[-1]
                groups[-1] = (last_c+char, (start, idx))

        return groups

            

    