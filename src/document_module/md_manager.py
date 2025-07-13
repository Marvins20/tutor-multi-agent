from document_module.md_parser import BLOCK_ITEMS, SUBTYPE_ITEMS, TEXT_ITEMS, MarkdownParser
import json


class MarkdownManager:
    def __init__(self):
        pass

    def get_text_at_line(self, target_line, ast):
        element = self._find_text(target_line, 0, ast)
        if element:
            return (element[0], element[1])
        return ("", None)

    def get_block_at_line(self,target_line, ast): 
        element = self._find_block(target_line, 0, ast)
        if not element[0]:
            print("O bloco da linha ", target_line, "não foi encontrado.")
            return ("", None)
        
        return (self.colapse_text(element[0]),element[1], element[2])
        

    def rewrite_text_at_line(self, line, element, ast):
        ast = self._rewrite_text(element,line,0,ast)
        return ast

    def rewrite_block_at_line(self, line, element, ast):
        ast = self._rewrite_block(element, line, 0, ast)
        return ast
    
    def insert_after_line(self, line, element ,ast):
        ast = self._insert_after_text_by_line(element, line, 0, ast)
        return ast
    
    def insert_after_block(self, line, element, ast ):
        ast = self._insert_after_block_by_line(element,line, 0, ast)[0]
       
        return ast
    
    def colapse_text(self, element):
        text = ""
        for child in element["children"]:
            if child["type"] in TEXT_ITEMS:
                text += (child["content"] + "\n")
            else:
                text += self.colapse_text(child)
        return text

    def _find_text(self, target_line, line_index, element):
        for idx,child in enumerate(element["children"],1):

            current_line = line_index + child["line_count"]
            if target_line <= current_line:
                if child["type"] in TEXT_ITEMS:
                    types = [(subtext["type"], (subtext["start"],subtext["end"])) for subtext in child["children"]]
                    return (child["content"], types)
                return self._find_text(target_line, line_index, child)
            line_index = current_line
            
        
        return ["", None]

    def _find_block(self, target_line, line_index, element):
        for idx, child in enumerate(element["children"],1):
            current_line = line_index + child["line_count"]
            # print("---chld:",idx,"_lindex:",child["line_number"],idx,"_tgt:",target_line,"__current:",current_line,"__content:", child["content"])

            if target_line <= current_line:
                if child["type"] in BLOCK_ITEMS and child["children"]:
                    result = self._find_block(target_line, line_index, child)
                   
                    return result
                return (element, element["type"], element["class"])
            line_index = current_line
        return (element, element["type"], element["class"])

    #TODO not working
    def _rewrite_text(self, new_element, target_line, line_index, element):
        for idx, child in enumerate(element["children"],1):
            current_line = line_index + child["line_count"]
            if target_line < current_line:
                if child["type"] in TEXT_ITEMS:
                    element["children"][idx] = new_element
                    return element
                self._rewrite_text(element, target_line, line_index, child)
                return element
            line_index = current_line
        return element
    
    def _rewrite_block(self, new_element, target_line, line_index, element):
        for idx, child in enumerate(element["children"],1):
            current_line = line_index + child["line_count"]
            print("---chld:",idx,"_lindex:",child["line_number"],idx,"_tgt:",target_line,"__current:",current_line,"__content:", child["content"])
            if target_line < current_line:
                if child["type"] in BLOCK_ITEMS:
                    element["children"][idx] = self._rewrite_block(new_element, target_line, line_index, child)
                    return element
                else:
                    return new_element
            line_index = current_line
        return element

    def _insert_after_text_by_line(self, elem_to_insert, target_line, line_index, element ):
        for idx, child in enumerate(element["children"],1):
            current_line = line_index + child["line_count"]
            if target_line <= current_line:
                if child["type"] in TEXT_ITEMS:
                    element["children"].insert(idx, elem_to_insert)
                    return element
                element[idx] = self._insert_after_text_by_line(elem_to_insert,target_line, line_index, child )
                return element
            line_index = current_line
        return element

    def _insert_after_block_by_line(self, elem_to_insert, target_line, line_index, element):
        for idx, child in enumerate(element["children"],1):
            current_line = line_index + child["line_count"]
            if target_line <= current_line:
                if child["type"] in BLOCK_ITEMS:
                    result = self._insert_after_block_by_line(elem_to_insert, target_line, line_index, child)
                    if result[1]:
                        element["children"].insert(idx, elem_to_insert)
                    return [element, False]
                print("-----------------------achou", element["content"])
                return [element, True]
            line_index = current_line
        return [element, False]        

    


# file_content = ""
# with open("/Users/marcusabr/Documents/AI Journey/começo.md", 'r', encoding='utf-8') as file:
#     file_content = file.read()


# with open("/Users/marcusabr/Dev/introduction-ai/tutor-agent/file.md", 'r', encoding='utf-8') as file:
#     file_content = file.read()

# parser = MarkdownParser()

# result = parser.parse(file_content)
# with open("parsed_result.json", 'w', encoding='utf-8') as output_file:
#     json.dump(result, output_file, indent=4, ensure_ascii=False)

# line = 7

# manager = MarkdownManager()
# block = manager.get_block_at_line(line, result)
# text = manager.get_text_at_line(line, result)
# print(text)
# print(block[0])
# new_elem = parser.parse("\n Essa é a sua resposta \n esse é o segundo parágrafo a\n\n")
# new_elem2 = parser.parse("\n mentiraaaaaaaaaa\n")
# # result = manager.insert_after_block(line, new_elem, result)
# # result = manager.insert_after_line(15, new_elem, result)s
# result = manager.rewrite_block_at_line(2, new_elem2, result)
# with open("parsed_new.json", 'w', encoding='utf-8') as output_file:
#     json.dump(result, output_file, indent=4, ensure_ascii=False)
# print(manager.colapse_text(result))




# # # # manager.rewrite_block_at_line(29, new_elem, result)
# # # new_elem = parser.parse("- [x] China pae\n")
# # # manager.append_text_after_line(34, new_elem, result )
# with open("parsed_result.json", 'w', encoding='utf-8') as output_file:
#     json.dump(result, output_file, indent=4, ensure_ascii=False)

# finder = MarkdownFinder()
# print("-------------")
# response = finder.get_text_at_line(0, result)
# print(response)