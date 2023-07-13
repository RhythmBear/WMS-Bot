from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Define a class that handles file events
class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        # This method is called when a file is created (i.e., download started)
        print("File download started:", event.src_path)

    def on_modified(self, event):
        # This method is called when a file is modified (including after writing, i.e., download completed)
        print("File download completed:", event.src_path)


# Create an instance of the file event handler
file_handler = FileEventHandler()

# Create an observer
observer = Observer()

# Schedule the file event handler to watch the download directory
observer.schedule(file_handler, path=r'C:\Users\Windows\Downloads', recursive=True)

# Start the observer
observer.start()

# Keep the observer running until interrupted
try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()

# Wait for the observer to complete
observer.join()
