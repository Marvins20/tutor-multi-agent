from dataclasses import dataclass
from typing import List, Tuple

from mtypes.changes import TextChange


@dataclass
class DocumentChange:
    class_name: str
    file_path: str
    line_number: int
    content: str
    modified_text: List[TextChange]
    affected_subtypes: List[str]
    block: Tuple[str, str]
    context: str