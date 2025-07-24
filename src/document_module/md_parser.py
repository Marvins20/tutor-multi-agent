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
    "list_item",
    "empty"
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
    "#EVAL",
    "#QST",
    "#NXT"
]

class MarkdownParser:
    def __init__(self):
        self.contextStack = []
        self.id_dict = {}

    def parse(self, plain_text):
        lines = plain_text.split("\n")
        self.contextStack.append({"class":"root","type": "root", "content": "", "line_count":0,"line_number":0,  "children": []})
        
        for idx, line in enumerate(lines):
            self.match_line(line, idx+1)
        
        mdAST = {}
        while  self.contextStack:
            mdAST = self.popContext()
        return mdAST

    def match_line(self, line, idx):
        # Don`t process when inside a code block
        # Code block   
        if line.strip().startswith("```"):
            if(self.contextStack[0]["type"] ==  "block_code"):
                self.pushLineToContext({"class":"bcend", "type": "end_block_code", "content": line, "line_count":1, "line_number":idx, "children": []})
                self.popContext()
                return
            
            self.pushContext( {"class":"bcode", "type": "block_code", "content": "", "line_count":0, "line_number":idx,"children": []})
            self.pushLineToContext({"class":"bcstr", "type": "start_block_code", "content": line, "line_count":1, "line_number":idx,"children": []})
            return

        if(self.contextStack[0]["type"] == "block_code"):
            self.pushLineToContext({"class":"bctxt", "type": "text", "content": line, "line_count":1, "line_number":idx,"children": []})
            return

        # List
        if line.strip().startswith("- ") or re.match(r'^\d+\.\s', line):
            leading_whitespace_level = self.count_leading_whitespace(line)
            if(self.contextStack[0]["type"] != "block_list" or 
            (self.contextStack[0]["leading_whitespace_level"] < leading_whitespace_level)):
                self.pushContext({"class":"blist", "type": "block_list", "content": "", "leading_whitespace_level": leading_whitespace_level, "line_count": 0, "line_number":idx,"children": []})
            
            children = self.search_patterns_in_text(line)
            self.pushLineToContext({"class":"blln","type": "list_item", "content": line, "line_count": 1, "line_number":idx,"children": children})
            return

        # Close the context if the next element is not a block item
        if(self.contextStack[0]["type"] == "block_list"):
            self.popContext()

        # Empty line
        if line.strip() == "":
            self.pushLineToContext({"class":"vd", "type": "empty", "content": line, "line_count":1, "line_number":idx,"children": []})
            return

        # Text hightlight
        if line.strip().startswith(">"):
            sub_element = {"class":"bimpt", "type": "text", "content": line, "line_count":1, "line_number":idx,"children": []}
            self.pushLineToContext({"class":"bimp", "type": "block_highlight", "content": line, "line_count":1, "line_number":idx,"children": [sub_element]})
            return

        # Defined keywords for specific behaviors
        if self.line_starts_with_keyword(line.strip()):
            if(self.contextStack[0]["type"] ==  "block_keyword"):
                self.popContext()
            self.pushContext({"class":"bkey","type": "block_keyword", "content": line, "line_count": 1, "line_number":idx,"children": []})
            self.pushLineToContext({"class":"bkeyt", "type": "text", "content": line, "line_count": 1, "line_number":idx,"children": []})
            return

        # Divisors
        if line.strip().startswith("---"):
            if(self.contextStack[0]["type"] ==  "block_keyword"):
                self.pushLineToContext({"class":"div", "type": "text", "content": line, "line_count": 1, "line_number":idx,"children": []})
                return
            self.popContext()
            self.pushContext({"class":"bdiv", "type": "block_division", "content": line, "line_count": 1, "line_number":idx,"children": []})
            self.pushLineToContext({"class":"div", "type": "text", "content": line, "line_count": 1, "line_number":idx,"children": []})
            return

        # Heading processing
        if re.match(r'^(#+)\s', line.strip()):
            heading_level = len(re.match(r'^#*', line).group(0))
            while self.contextStack[0]["type"]=="heading":
                if heading_level >= self.contextStack[0]["heading_level"]:
                    self.popContext()
                else:
                    break
            self.pushContext({"class":"bhead", "type": "heading", "content": line, "heading_level": heading_level, "line_count": 1,  "line_number":idx,"children": []})
            self.pushLineToContext({"class":"bheadt", "type": "text", "content": line, "line_count": 1, "line_number":idx,"children": []})
            return 

        # Process regular text lines
        children = self.search_patterns_in_text(line)
        self.pushLineToContext({"class":"tx","type": "text", "content": line, "line_count":1, "line_number":idx,"children": children})
        return

    def pushContext(self, element):
        if self.contextStack:
            element["class"]+=("-"+self.contextStack[0]["class"])
        self.contextStack.insert(0, element)
        return element        

    def pushLineToContext(self, element):
        if not self.contextStack:
            raise Exception("Context stack is empty")

        element["class"]+=("-"+self.contextStack[0]["class"])     
        self.contextStack[0]["children"].append(element)
        return element

    def popContext(self):
        element = self.contextStack.pop(0)
        element["line_count"] = sum(child["line_count"] for child in element.get("children", []))
        if self.contextStack:
            self.pushLineToContext(element)
        return element
    

    def search_patterns_in_text(self, text):
        results = []
        self.patterns = {
            'link': r'\[([^\]]+)\]\(([^)]+)\)',  # Matches [text](url)
            'image': r'!\[([^\]]+)\]\(([^)]+)\)',  # Matches ![alt text](url)
            'question': r'\[\[\s*(.*?)\s*\]\]',
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
    
    def count_leading_whitespace(self, line):
        original_length = len(line)
        stripped_length = len(line.lstrip())
        return original_length - stripped_length

    def line_starts_with_keyword(self, line):
        return any(line.strip().startswith(keyword) for keyword in KEYWORDS)
    
