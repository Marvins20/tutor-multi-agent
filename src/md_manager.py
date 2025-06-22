from md_parser import BLOCK_ITEMS, SUBTYPE_ITEMS, TEXT_ITEMS, MarkdownParser
import json


class MarkdownManager:
    def __init__(self):
        pass

    def get_text_at_line(self, target_line, ast):
        element = self.find_text(target_line, 0, ast)
        if element:
            return element["content"]
        return ""

    def get_block_at_line(self,target_line, ast): 
        element = self.find_block(target_line, 0, ast)
        if element:
            a = self.colapse_text(element)
            print(a)
            return self.colapse_text(element)
        return ""

    def get_context_at_line(self,target_line, ast):
        return self.find_and_collapse_block("",target_line,0,ast)

    def rewrite_block_at_line(self, line, text, ast):
        ast = self.rewrite_block(text, line, 0, ast)
        return self.colapse_text(ast)

    def rewrite_text_at_line(self, line, text, ast):
        ast = self.rewrite_text(text,line,0,ast)
        return self.colapse_text(ast)

    def find_text(self, target_line, line_index, element):
        for child in element["children"]:
            current_line = line_index + child["line_count"]
            if target_line <= current_line:
                # print(current_line, " ", target_line, " ", child["content"])
                if child["type"] in TEXT_ITEMS:
                    return child
                return self.find_text(target_line, line_index, child)
            line_index = current_line
        return None

    def find_block(self, target_line, line_index, element):
        for child in element["children"]:
            current_line = line_index + child["line_count"]
            if target_line < current_line:
                if child["type"] in TEXT_ITEMS:
                    return element
                return self.find_block(target_line, line_index, child)
            line_index = current_line
        return None
    
    # TODO not precise
    def find_and_collapse_block(self, text, target_line, line_index, element):
        for child in element["children"]:
            current_line = line_index + child["line_count"]
            if target_line < current_line:
                if child["type"] in TEXT_ITEMS:
                    return text + self.colapse_text(element)
                return text + self.find_and_collapse_block(target_line, line_index, child)
            text += child["content"]
            line_index = current_line
        return ""

    def rewrite_text(self, text, target_line, line_index, element):
        for idx, child in enumerate(element["children"]):
            current_line = line_index + child["line_count"]
            if target_line < current_line:
                if child["type"] in TEXT_ITEMS:
                    element["children"][idx] = {"type": "unprocessed", "content": text, "line_count":0, "block_line_count": 0, "children": []}
                    return element
                self.rewrite_block(text, target_line, line_index, child)
                return element
            line_index = current_line
        return element
    
    def rewrite_block(self, text, target_line, line_index, element):
        for idx, child in enumerate(element["children"]):
            current_line = line_index + child["line_count"]
            if target_line < current_line:
                if child["type"] in TEXT_ITEMS:
                    return {"type": "unprocessed", "content": text, "line_count":0, "block_line_count": 0, "children": []}
                element["children"][idx] = self.rewrite_block(text, target_line, line_index, child)
                return element
            line_index = current_line
        return element


    def colapse_text(self, element):
        text = element["content"] + "\n"
        for child in element["children"]:
            if child["type"] in TEXT_ITEMS:
                text += (child["content"] + "\n")
            else:
                text += self.colapse_text(child)
        return text

# file_content = ""
# with open("/Users/marcusabr/Dev/introduction-ai/tutor-agent/file.md", 'r', encoding='utf-8') as file:
#     file_content = file.read()

# result = MarkdownParser().parse(file_content)
# print(json.dumps(result, indent=4, ensure_ascii=False))

# finder = MarkdownFinder()
# print("-------------")
# response = finder.get_text_at_line(0, result)
# print(response)