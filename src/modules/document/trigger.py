from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

from decorators import debounce, filter_files
from decide import safe_make_decision
from document_module import DocumentModule
from comparator import Comparator
from md_parser import MarkdownParser
from md_manager import MarkdownManager
from semantic_block import SemanticBlock, SentenceType



class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, document_module:DocumentModule):
        self.document_module = document_module
        super().__init__()

    @filter_files(extensions_to_filter=[".md"], filterDirectory=True)
    def on_created(self, event):
        print(f"Created: {event.src_path}")

    @filter_files(extensions_to_filter=[".md"], filterDirectory=True)
    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")

    @debounce(wait=2)
    @filter_files(extensions_to_filter=[".md"])
    def on_modified(self, event):
        #TODO conectar com environment context queue, enviando as mudanças para la
        modified = self.document_module.check_file_last_change(event.src_path)
        print(modified)

    @filter_files(filterDirectory=True)
    def on_moved(self, event):
        print(f"Moved: {event.src_path} to {event.dest_path}")

if __name__ == "__main__":
    # Replace this path with the folder you want to monitor
    folder_to_monitor = "/Users/marcusabr/Documents/AI Journey"

    event_handler = FolderChangeHandler(DocumentModule(Comparator(),MarkdownParser(), MarkdownManager() ))
    observer = Observer()
    observer.schedule(event_handler, folder_to_monitor, recursive=True)

    print(f"Starting folder monitoring on: {folder_to_monitor}")
    observer.start()
    
    try:
        # Keep the script running to listen for events
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()