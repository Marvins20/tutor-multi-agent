from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class TextChange:
    text: str
    location: Tuple[int, int]

@dataclass
class LineChange:
    line_number: int
    content: str
    text_changes: List[TextChange]