# /Users/marcusabr/Dev/introduction-ai/tutor-agent/src/file_index.py

class FileIndex:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_content = ""
        self.index = self.build_index()

    def build_index(self):
        """
        Build an index that maps line numbers to paragraphs.
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        self.file_content = file_content
        paragraphs = self.extract_paragraphs(file_content)
        return self.create_line_to_paragraph_index(paragraphs)

    def extract_paragraphs(self, file_content):
        """
        Extract paragraphs and their line numbers from file content.
        Args:
            file_content (str): Content of the file
        Returns:
            dict: Dictionary containing paragraphs and their line numbers
        """
        paragraphs = {}
        current_paragraph = []
        current_line_numbers = []

        lines = file_content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # If line is empty and we have content in current paragraph
            if not line and current_paragraph:
                # Join paragraph lines and store with line numbers
                paragraph_text = '\n'.join(current_paragraph)
                paragraphs[paragraph_text] = current_line_numbers
                # Reset for next paragraph
                current_paragraph = []
                current_line_numbers = []
            # If line has content, add to current paragraph
            elif line:
                current_paragraph.append(line)
                current_line_numbers.append(line_num)

        # Add last paragraph if exists
        if current_paragraph:
            paragraph_text = '\n'.join(current_paragraph)
            paragraphs[paragraph_text] = current_line_numbers

        return paragraphs

    def create_line_to_paragraph_index(self, paragraphs):
        """
        Create an index that maps line numbers to paragraphs.
        Args:
            paragraphs (dict): Dictionary containing paragraphs and their line numbers
        Returns:
            dict: Dictionary mapping line numbers to paragraphs
        """
        line_to_paragraph_index = {}
        for paragraph, line_numbers in paragraphs.items():
            for line_number in line_numbers:
                line_to_paragraph_index[line_number] = paragraph
        return line_to_paragraph_index

    def get_paragraph_for_line(self, line_number):
        """
        Get the paragraph for a given line number.
        Args:
            line_number (int): Line number
        Returns:
            str: Paragraph text
        """
        return self.index.get(line_number, None)



