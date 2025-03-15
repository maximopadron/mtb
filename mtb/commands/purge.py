import click
import os
import re
import time
from mtb.utils import logger, file_utils, config_parser
from mtb.utils.decorators import log_header_footer

log = logger.get_logger()

def get_configs(filepath, compress_days, delete_days, recursive):
    """
    Merge CLI parameters with the purge configuration.
    If CLI parameters are provided, use them; otherwise, load from file.
    """
    if filepath and compress_days is not None and delete_days is not None:
        return {filepath: {"compress": compress_days, "delete": delete_days, "recursive": recursive}}
    else:
        configs = config_parser.load_config("purge.yaml") or {}
        for pattern in configs:
            configs[pattern]["recursive"] = recursive
        return configs

def find_files(pattern, recursive):
    """Return a list of files matching 'pattern', searching recursively if requested."""
    if recursive:
        return [
            os.path.join(root, f)
            for root, _, files in os.walk(".")
            for f in files
            if re.match(pattern, os.path.join(root, f))
        ]
    else:
        return [
            os.path.join(".", f)
            for f in os.listdir(".")
            if os.path.isfile(os.path.join(".", f)) and re.match(pattern, os.path.join(".", f))
        ]

def get_file_age(f, current_time):
    """Return the age of file f in days, or None if error."""
    try:
        return (current_time - os.path.getmtime(f)) / (24 * 3600)
    except Exception as e:
        log.error(f"Error getting age for {f}: {e}")
        return None

def try_delete_file(f, age_days):
    """Attempt to delete the file and log the result."""
    try:
        os.remove(f)
        log.info(f"Deleted {f} (age {age_days:.2f} days)")
    except Exception as e:
        log.error(f"Error deleting {f}: {e}")

def try_compress_file(f, age_days):
    """Attempt to compress the file and log the result."""
    try:
        compressed = file_utils.compress_file(f)
        log.info(f"Compressed {f} to {compressed} (age {age_days:.2f} days)")
    except Exception as e:
        log.error(f"Error compressing {f}: {e}")

def process_files(files, current_time, compress_threshold, delete_threshold):
    """
    For each file, compute its age (in days) and:
      - Delete if age >= delete_threshold.
      - Otherwise, compress if age >= compress_threshold and if the file is not already compressed.
    """
    for f in files:
        age_days = get_file_age(f, current_time)
        if age_days is None:
            continue
        if age_days >= delete_threshold:
            try_delete_file(f, age_days)
        elif age_days >= compress_threshold and not (f.endswith('.zip') or f.endswith('.gz')):
            try_compress_file(f, age_days)

@click.command(name="purge", help="Delete old files and compress remaining ones based on age thresholds.")
@click.option('--filepath', default=None, help="Path to target files (overrides config).")
@click.option('--compress-days', default=None, type=int, help="File age in days to compress (overrides config).")
@click.option('--delete-days', default=None, type=int, help="File age in days to delete (overrides config).")
@click.option('--recursive', is_flag=True, help="Search for matching files recursively.")
@log_header_footer
def purge_cmd(filepath, compress_days, delete_days, recursive):
    """
    Purge command: delete files older than a delete threshold and compress files older than a compress threshold.
    
    CLI options override the configuration loaded from the purge config file.
    """
    current_time = time.time()
    configs = get_configs(filepath, compress_days, delete_days, recursive)
    for pattern, params in configs.items():
        files = find_files(pattern, params.get("recursive", False))
        process_files(files, current_time, params["compress"], params["delete"])
    log.info("Purge command completed.")

if __name__ == "__main__":
    purge_cmd()
