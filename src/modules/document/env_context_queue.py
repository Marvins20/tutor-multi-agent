from typing import List
from modules.document.document_module import DocumentChange
from semantic_block import SemanticBlock, SentenceType
class EnvironmentContextQueue:
    def __init__(self):
        self.contextQueue = []

    def pushInteractions(self, interactions: List[DocumentChange]):
        infer_sentence_type()
        # via receber um bloco de mudança
        #vai agrupar elas (ver se faz aqui ou no document module)
        #vai inferiri o tipo de senten;a
        for interaction in interactions:
            sentence_type = self.infer_sentence_type(interaction.types, interaction.content, interaction.path)
            context = SemanticBlock(
                origin_file_path=interaction.file_path,
                last_change= ,
                block= ,
                location=, 
                context=,
                sentence_type=sentence_type
            )
            self.contextQueue.append(context)  # Append interaction to the context queue

    def popInteraction(self):
        self.refineInteractinStack()
        return self.contextQueue.pop() if self.interactionStack else None

    def refineInteractionStack(self):
        # TODO for the line it is considered only the last change
        # TODO for Block, check if it is the same, and if it is, append to the text of the changes
        # TODO what about the specific changes in the line?
            #it should check if the file already exits
        pass

    def infer_sentence_type(self, types, content, path):
        if "block_highlight" in types:
            #quantas vezes voltou no mesmo imperative?
            #olgar apara todo um campo, identificar de verdade o que foi feito
            return SentenceType.IMPERATIVE

            #definir estruturade mapeamento dos arquivos
        elif "question"in types and path not in self.file_index:
            return SentenceType.INTERROGATIVE
            # e a resposta da IA, n vai sobrescrever?
            # verificar se respondeu de verdade
        elif "block_keyword" in types and content.startswith("#Question"):
            return SentenceType.ANSWER
            # verificar se respondeu de verdadde
        elif "block_keyword"in types and content.startswith("#Evaluation"):
            return SentenceType.EVALUATIVE
        else:
            return SentenceType.DECLARATIVE

    def block_significative_changes(self, changes):
        filtered_changes = [change for change in changes if change[1].strip() != "" ]
        if not filtered_changes:
            return None
        
        visit_values = [change[0] for change in filtered_changes]
        min_visit = min(visit_values)
        max_visit = max(visit_values)
        
        full_changes = '\n'.join(change[1] for change in changes)

        return ((min_visit, max_visit), full_changes)     