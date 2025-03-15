import click
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mtb.utils import logger
from mtb.utils.decorators import log_header_footer
from mtb.utils.time_utils import parse_interval

log = logger.get_logger()

class WatcherHandler(FileSystemEventHandler):
    def __init__(self, min_size, max_size):
        self.min_size = min_size
        self.max_size = max_size

    def on_created(self, event):
        log.info(f"File created: {event.src_path}")

    def on_deleted(self, event):
        log.info(f"File deleted: {event.src_path}")

@click.command(name="file-watcher", help="Watch a directory for file creation/deletion events with various filters.")
@click.option('-d', '--directory', default='.', help="Directory to watch.")
@click.option('-s', '--min-size', default=0, type=int, help="Minimum file size in bytes.")
@click.option('-S', '--max-size', default=float('inf'), type=float, help="Maximum file size in bytes.")
@click.option('-f', '--min-files', default=1, type=int, help="Minimum number of files.")
@click.option('-F', '--max-files', default=1, type=int, help="Maximum number of files.")
@click.option('-a', '--min-age', default=60, type=int, help="Minimum age of files in seconds (default 1 minute).")
@click.option('-A', '--max-age', default=float('inf'), type=float, help="Maximum age of files in seconds.")
@click.option('-m', '--move-to', default=None, help="Path to move the file(s).")
@click.option('-c', '--copy-to', default=None, help="Path to copy the file(s).")
@click.option('-e', '--remove-extension', is_flag=True, help="Remove the last extension of the file(s).")
@click.option('-l', '--limit', default="1h", help="Limit to watch for the file (e.g., 1d or 3h30m45s).")
@log_header_footer
def file_watcher_cmd(directory, min_size, max_size, min_files, max_files, min_age, max_age,
                     move_to, copy_to, remove_extension, limit):
    """
    Watch a directory and log events when files are created or deleted.
    """
    limit_seconds = parse_interval({limit})
    event_handler = WatcherHandler(min_size, max_size)
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()
    log.info(f"Started file watcher on {directory} with limit {limit}")

    try:
        time.sleep(limit_seconds)
    except KeyboardInterrupt:
        observer.stop()
    observer.stop()
    observer.join()
    log.info("File watcher stopped")
