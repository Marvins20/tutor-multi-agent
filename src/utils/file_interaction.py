import json
import os

current_file_path = os.path.abspath(__file__)
src_dir = os.path.dirname(os.path.dirname(current_file_path))  # Sobe um nível para apontar para /src
# Cria um caminho para 'my_file.txt' relativo ao diretório do script



def write_dict_to_json_file(file_name, dict):
    with open(file_name, 'w', encoding='utf-8') as output_file:
        json.dump(dict, output_file, indent=4, ensure_ascii=False)

def read_relative_file_content(file_name):
    file_path = os.path.join(src_dir, file_name)
    with open(file_path, 'r', encoding='utf-8') as input_file:
        return input_file.read()

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as input_file:
        return input_file.read()

def create_file_within_dir(file_name, content=""):
    
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w') as f:
        f.write(content)

def read_json_file_to_dict(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)