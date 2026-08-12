import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from scanner.file_scanner import scan_file


class FileMonitor(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        print("\n[NEW FILE]")
        print(event.src_path)

        scan_file(event.src_path)

    def on_modified(self, event):

        if event.is_directory:
            return

        print("\n[MODIFIED FILE]")
        print(event.src_path)

        scan_file(event.src_path)

    def on_moved(self, event):

        if event.is_directory:
            return

        print("\n[MOVED FILE]")
        print(event.dest_path)

        scan_file(event.dest_path)


def start_monitor(folders):

    observer = Observer()

    handler = FileMonitor()

    for folder in folders:

        if os.path.exists(folder):

            observer.schedule(
                handler,
                folder,
                recursive=True
            )

            print(f"Monitoring : {folder}")

    observer.start()

    print("\nContinuous Monitoring Started...\n")

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

    observer.join()