from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

from decorators import debounce, filter_files
from decide import safe_make_decision
from change_detector import FileChangeDetector

#TODO invert the dependence of the trigger, find ideal design pattern

class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, change_detector:FileChangeDetector):
        self.change_detector = change_detector
        super().__init__()

    @filter_files(extensions_to_filter=[".md"], filterDirectory=True)
    def on_created(self, event):
        print(f"Created: {event.src_path}")

    @filter_files(extensions_to_filter=[".md"], filterDirectory=True)
    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")

    @debounce(wait=3)
    @filter_files(extensions_to_filter=[".md"])
    def on_modified(self, event):
        print(f"Modified: {event.src_path}")
        modified = self.change_detector.compare_file_content(event.src_path)
        print(safe_make_decision(modified))

    @filter_files(filterDirectory=True)
    def on_moved(self, event):
        print(f"Moved: {event.src_path} to {event.dest_path}")

if __name__ == "__main__":
    # Replace this path with the folder you want to monitor
    folder_to_monitor = "/Users/marcusabr/Documents/AI Journey"

    event_handler = FolderChangeHandler(FileChangeDetector())
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