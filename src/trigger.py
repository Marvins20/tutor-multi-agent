# from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

from env_context_queue import EnvironmentContextQueue
from utils.decorators import debounce, filter_files
from document_module.document_module import DocumentModule
from document_module.comparator import Comparator
from document_module.md_parser import MarkdownParser
from document_module.md_manager import MarkdownManager



class FolderEventTrigger(FileSystemEventHandler):
    def __init__(self, document_module:DocumentModule, env_context: EnvironmentContextQueue):
        self.document_module = document_module
        self.env_context = env_context
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
        print(f"Deleted: {event.src_path}")
        modified = self.document_module.check_file_last_change(event.src_path)
        self.env_context.push_interactions(modified)


    @filter_files(filterDirectory=True)
    def on_moved(self, event):
        print(f"Moved: {event.src_path} to {event.dest_path}")

# if __name__ == "__main__":
#     # Replace this path with the folder you want to monitor
#     folder_to_monitor = "/Users/marcusabr/Documents/AI Journey"

#     event_handler = FolderEventTrigger(DocumentModule(Comparator(),MarkdownParser(), MarkdownManager() ), EnvironmentContextQueue())
#     observer = Observer()
#     observer.schedule(event_handler, folder_to_monitor, recursive=True)

#     print(f"Starting folder monitoring on: {folder_to_monitor}")
#     observer.start()
    
#     try:
#         # Keep the script running to listen for events
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()

#     observer.join()