
import hashlib
from watchdog.observers import Observer
import time
import asyncio

from agents.director.step_manager import StepManager
from env_context_queue import EnvironmentContextQueue
from document_module.document_module import DocumentModule
from document_module.comparator import Comparator
from document_module.md_parser import MarkdownParser
from document_module.md_manager import MarkdownManager

from agents.director.director_agent import DirectorAgent

from logger import Logger
from trigger import FolderEventTrigger

path = "/Users/marcusabr/Documents/AI Journey"

async def main():
    folder_to_monitor = sys.argv[1]
    environment_queue = EnvironmentContextQueue()
    document_module = DocumentModule(Comparator(), MarkdownParser(), MarkdownManager())
    document_module.start(path)
    event_handler = FolderEventTrigger(document_module, environment_queue)
    
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
# 
    print(f"Starting folder monitoring on: {path}")
    # Create a unique ID based on the hash of the monitored path
    logger_id = hashlib.md5(path.encode()).hexdigest()
    logger =  Logger()
    logger.set_id(logger_id)

    observer.start()

    director_agent = DirectorAgent(folder_to_monitor, environment_queue, StepManager(path))
    director_agent.start()
    
    try:
        while True:
            await director_agent.update()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: src/python tutor.py <path_to_tutoring_folder>")
        sys.exit(1)
    
    import sys
    asyncio.run(main())

    