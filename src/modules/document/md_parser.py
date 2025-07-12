import re
import uuid

BLOCK_ITEMS = [
    "heading",
    "block_code",
    "block_highlight",
    "block_keyword",
    "block_division"
]

TEXT_ITEMS = [
    "text",
    "list_item"
]

SUBTYPE_ITEMS = [
    "link",
    "image",
    "question",
    "bold",
    "italic",
    "tag",
]

KEYWORDS = [
    "#Question",
    "#Evaluation"
]

class MarkdownParser:
    def __init__(self):
        self.contextStack = []

    def parse(self, plain_text):
        lines = plain_text.split("\n")
        self.contextStack.append({"type": "root", "content": "", "line_count":0,  "children": []})
        
        for line in lines:
            self.match_line(line)
        
        mdAST = {}
        while  self.contextStack:
            mdAST = self.popContext()
        return mdAST

    def match_line(self, line):
        # Don`t process when inside a code block
        # Code block   
        if line.strip().startswith("```"):
            if(self.contextStack[0]["type"] ==  "block_code"):
                self.pushLineToContext({"type": "end_block_code", "content": line, "line_count":1, "children": []})
                self.popContext()
                return
            
            self.pushContext( {"type": "block_code", "content": "", "line_count":0, "children": []})
            self.pushLineToContext({"type": "start_block_code", "content": line, "line_count":1, "children": []})
            return

        if(self.contextStack[0]["type"] == "block_code"):
            self.pushLineToContext({"type": "text", "content": line, "line_count":1, "children": []})
            return

        # List
        if line.strip().startswith("- ") or re.match(r'^\d+\.\s', line):
            leading_whitespace_level = self.count_leading_whitespace(line)
            if(self.contextStack[0]["type"] != "block_list" or 
            (self.contextStack[0]["leading_whitespace_level"] < leading_whitespace_level)):
                self.pushContext({"type": "block_list", "content": "", "leading_whitespace_level": leading_whitespace_level, "line_count": 0, "children": []})
            
            children = self.search_patterns_in_text(line)
            self.pushLineToContext({"type": "list_item", "content": line, "line_count": 1, "children": children})
            return

        # Close the context if the next element is not a block item
        if(self.contextStack[0]["type"] == "block_list"):
            self.popContext()

        # Empty line
        if line.strip() == "":
            self.pushLineToContext({"type": "empty", "content": line, "line_count":1, "children": []})
            return

        # Text hightlight
        if line.strip().startswith(">"):
            children  = self.search_patterns_in_text(line)
            self.pushLineToContext({"type": "block_highlight", "content": line, "line_count":1, "children": children})
            return

        # Defined keywords for specific behaviors
        if self.line_starts_with_keyword(line.strip()):
            if(self.contextStack[0]["type"] ==  "block_keyword"):
                self.popContext()
            self.pushContext({"type": "block_keyword", "content": line, "line_count": 1, "children": []})
            self.pushLineToContext({"type": "text", "content": line, "line_count": 1, "children": []})
            return

        # Divisors
        if line.strip().startswith("---"):
            if(self.contextStack[0]["type"] ==  "block_keyword"):
                self.pushLineToContext({"type": "text", "content": line, "line_count": 1, "children": []})
                return
            self.popContext()
            self.pushContext({"type": "block_division", "content": line, "line_count": 1, "children": []})
            return

        # Heading processing
        if line.strip().startswith("# "):
            heading_level = len(re.match(r'^#*', line).group(0))
            while self.contextStack[0]["type"]=="heading":
                if heading_level >= self.contextStack[0]["heading_level"]:
                    self.popContext()
                else:
                    break
            self.pushContext({"type": "heading", "content": line, "heading_level": heading_level, "line_count": 1,  "children": []})
            self.pushLineToContext({"type": "text", "content": line, "line_count": 1, "children": []})
            return 

        # Process regular text lines
        children = self.search_patterns_in_text(line)
        self.pushLineToContext({"type": "text", "content": line, "line_count":1, "children": children})
        return

    def pushContext(self, element):
        element["id"] = str(uuid.uuid4().hex[:32])
        self.contextStack.insert(0, element)
        return element        

    def pushLineToContext(self, element):
        if not self.contextStack:
            raise Exception("Context stack is empty")        
        self.contextStack[0]["children"].append(element)
        return element

    def popContext(self):
        element = self.contextStack.pop(0)
        element["line_count"] = sum(child["line_count"] for child in element.get("children", [])) + element["line_count"]
        if self.contextStack:
            self.pushLineToContext(element)
        return element
    

    def search_patterns_in_text(self, text):
        results = []
        self.patterns = {
            'link': r'\[([^\]]+)\]\(([^)]+)\)',  # Matches [text](url)
            'image': r'!\[([^\]]+)\]\(([^)]+)\)',  # Matches ![alt text](url)
            'question': r'\[\[?\s*(.*?)\s*\]\]',
            'italic': r'(\*|_)(?!\1)[^\1]+(\1)',  # Matches *text* or _text_
            'bold': r'(\*{2}|_{2})(?!\1)[^\1]+(\1)',  # Matches **text** or __text__
            'tag': r'\B#\w+\b'
        }
        
        for pattern_name, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                results.append({
                    'type': pattern_name,
                    'content': match.group(),
                    'start': match.start(),
                    'end': match.end(),\
                    "line_count": 0, 
                    "children": []
                })
        
        return results        

        # results = []
        # for name,pattern in self.patterns.items():
        #     match = re.search(pattern, text)
        #     if match:
        #         results.append({"type": name, "content": match.group(), "line_count": 0, "children": []})
        # return results
    
    def count_leading_whitespace(self, line):
        original_length = len(line)
        stripped_length = len(line.lstrip())
        return original_length - stripped_length

    def line_starts_with_keyword(self, line):
        return any(line.strip().startswith(keyword) for keyword in KEYWORDS)
