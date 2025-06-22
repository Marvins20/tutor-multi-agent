import re

BLOCK_ITEMS = [
    "heading",
    "block_list",
    "block_code",
    "block_quote",
]

TEXT_ITEMS = [
    "text",
    "list_item"
]

SUBTYPE_ITEMS = [
    "link",
    "image",
    "file",
    "bold",
    "italic"
]

class MarkdownParser:
    def __init__(self):
        self.contextStack = []

    def parse(self, plain_text):
        lines = plain_text.split("\n")
        self.contextStack.append({"type": "root", "content": "", "line_count":0, "block_line_count": 0, "children": []})
        
        for line in lines:
            self.match_line(line)
        
        mdAST = {}
        while  self.contextStack:
            mdAST = self.popContext()
        return mdAST

    def match_line(self, line):
        if line.strip().startswith("-") or re.match(r'^\d+\.\s', line):
            leading_whitespace_level = self.count_leading_whitespace(line)
            if(self.contextStack[0]["type"] != "block_list" or 
            (self.contextStack[0]["leading_whitespace_level"] < leading_whitespace_level)):
                self.pushContext({"type": "block_list", "content": "", "leading_whitespace_level": leading_whitespace_level, "line_count": 0, "block_line_count": 0, "children": []})
            
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

        # Code block   
        if line.strip().startswith("```"):
            if(self.contextStack[0]["type"] ==  "block_code"):
                self.pushLineToContext({"type": "end_block_code", "content": line, "line_count":1, "children": []})
                self.popContext()
                return
            
            self.pushContext( {"type": "block_code", "content": "", "block_line_count": 0, "line_count":0, "children": []})
            self.pushLineToContext({"type": "start_block_code", "content": line, "line_count":1, "children": []})
            return

        # Text hightlight
        if line.strip().startswith(">"):
            children  = self.search_patterns_in_text(line)
            self.pushLineToContext({"type": "block_quote", "content": line, "line_count":1, "children": children})
            return

        # Heading processing
        if line.strip().startswith("#"):
            heading_level = len(re.match(r'^#*', line).group(0))
            while self.contextStack[0]["type"]=="heading":
                if heading_level >= self.contextStack[0]["heading_level"]:
                    self.popContext()
                else:
                    break
            self.pushContext({"type": "heading", "content": line, "heading_level": heading_level, "line_count": 1, "block_line_count": 1, "children": []})
            return

        # Process regular text lines
        children = self.search_patterns_in_text(line)
        self.pushLineToContext({"type": "text", "content": line, "line_count":1, "children": children})
        return

    def pushContext(self, element):
        self.contextStack.insert(0, element)
        return element        

    def pushLineToContext(self, element):
        if not self.contextStack:
            raise Exception("Context stack is empty")        
        self.contextStack[0]["children"].append(element)
        self.contextStack[0]["block_line_count"]+=1
        return element

    def popContext(self):
        element = self.contextStack.pop(0)
        element["line_count"] = sum(child["line_count"] for child in element.get("children", [])) + element["line_count"]
        if self.contextStack:
            self.pushLineToContext(element)
        return element
    

    def search_patterns_in_text(self, text):
        self.patterns = {
            'link': r'\[([^\]]+)\]\(([^)]+)\)',  # Matches [text](url)
            'image': r'!\[([^\]]+)\]\(([^)]+)\)',  # Matches ![alt text](url)
            'file': r'\[([^\]]+)\]',
            'italic': r'(\*|_)(?!\1)[^\1]+(\1)',  # Matches *text* or _text_
            'bold': r'(\*{2}|_{2})(?!\1)[^\1]+(\1)',  # Matches **text** or __text__
        }

        results = []
        for name,pattern in self.patterns.items():
            match = re.search(pattern, text)
            if match:
                results.append({"type": name, "content": match.group(), "line_count": 0, "children": []})
        return results
    
    def count_leading_whitespace(self, line):
        original_length = len(line)
        stripped_length = len(line.lstrip())
        return original_length - stripped_length
