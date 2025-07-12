from md_parser import BLOCK_ITEMS, SUBTYPE_ITEMS, TEXT_ITEMS, MarkdownParser
import json


class MarkdownManager:
    def __init__(self):
        pass

    def get_text_at_line(self, target_line, ast):
        element = self.find_text(target_line, 0, ast)
        if element:
            return (element[0], element[1])
        return ("", None)

    def get_block_at_line(self,target_line, ast): 
        element = self.find_block(target_line, 0, ast)
        if element:
            return (self.colapse_text(element[0]),element[1])
        return ("", None)

    def rewrite_text_at_line(self, line, element, ast):
        ast = self.rewrite_text(element,line,0,ast)
        return ast

    def rewrite_block_at_line(self, line, element, ast):
        ast = self.rewrite_block(element, line, 0, ast)
        return ast
    
    def append_text_after_line(self, line, element ,ast):
        ast = self.append_after_text(element, line, 0, ast)
        return ast
    
    def append_block_after_line(self, line, element, ast ):
        ast = self.append_after_block(element,line, 0, ast)
        return ast

    def find_text(self, target_line, line_index, element):
        for child in element["children"]:
            current_line = line_index + child["line_count"]
            if target_line <= current_line:
                if child["type"] in TEXT_ITEMS:
                    types = [(subtext["type"], (subtext["start"],subtext["end"])) for subtext in child["children"]]
                    return (child["content"], types)
                return self.find_text(target_line, line_index, child)
            line_index = current_line
            
        
        return ["", None]

    def find_block(self, target_line, line_index, element):
        
        for idx, child in enumerate(element["children"]):
            current_line = line_index + child["line_count"]
            # print("---chld:",idx,"_tgt:",target_line,"__current:",current_line)
            if target_line <= current_line:
                if child["type"] in BLOCK_ITEMS:
                    return self.find_block(target_line, line_index, child)
                # print("_______________achou_________________", element)
                return (element, element["type"])
            line_index = current_line
            # print(line_index, "{", self.colapse_text(child), "}")
        # print("chegou no None")
        return (None, None)

    def rewrite_text(self, new_element, target_line, line_index, element):
        for idx, child in enumerate(element["children"]):
            current_line = line_index + child["line_count"]
            if target_line < current_line:
                if child["type"] in TEXT_ITEMS:
                    element["children"][idx] = new_element
                    return element
                self.rewrite_text(element, target_line, line_index, child)
                return element
            line_index = current_line
        return element
    
    def rewrite_block(self, new_element, target_line, line_index, element):
        for idx, child in enumerate(element["children"]):
            current_line = line_index + child["line_count"]
            if target_line < current_line:
                if child["type"] in TEXT_ITEMS:
                    return new_element
                element["children"][idx] = self.rewrite_block(new_element, target_line, line_index, child)
                return element
            line_index = current_line
        return element

    def append_after_text(self, elem_to_insert, target_line, line_index, element ):
        for idx, child in enumerate(element["children"]):
            current_line = line_index + child["line_count"]
            if target_line <= current_line:
                if child["type"] in TEXT_ITEMS:
                    element["children"].insert(idx+1, elem_to_insert)
                    return element
                element[idx] = self.append_after_text(elem_to_insert,target_line, line_index, child )
                return element
            line_index = current_line
        return element

    def append_after_block(self, elem_to_insert, target_line, line_index, element):
        for idx, child in enumerate(element["children"]):
            current_line = line_index + child["line_count"]
            if target_line <= current_line:
                if child["type"] in BLOCK_ITEMS:
                    result = self.append_after_block(elem_to_insert, target_line, line_index, child)
                    if not isinstance(result, list):
                        result = [result]
                    element["children"] = (element["children"][:idx] + result + element["children"][idx:])
                    return element
                return [element, elem_to_insert]
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
# with open("/Users/marcusabr/Documents/AI Journey/começo.md", 'r', encoding='utf-8') as file:
#     file_content = file.read()


# # with open("/Users/marcusabr/Dev/introduction-ai/tutor-agent/file.md", 'r', encoding='utf-8') as file:
# #     file_content = file.read()

# parser = MarkdownParser()

# result = parser.parse(file_content)

# manager = MarkdownManager()
# block = manager.get_block_at_line(34, result)
# # # new_elem = parser.parse("#Question\n-----\n\nExercício 1\n\nQuem é china?\n\n\n- [x] China pae\n- [ ] Severion\n- [ ] Cabrunca\n- [ ] sepa\n\n")
# # # # manager.rewrite_block_at_line(29, new_elem, result)
# # # new_elem = parser.parse("- [x] China pae\n")
# # # manager.append_text_after_line(34, new_elem, result )
# with open("parsed_result.json", 'w', encoding='utf-8') as output_file:
#     json.dump(result, output_file, indent=4, ensure_ascii=False)
# print(block)

# finder = MarkdownFinder()
# print("-------------")
# response = finder.get_text_at_line(0, result)
# print(response)