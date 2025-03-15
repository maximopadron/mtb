import os
import platform
import shutil
import gzip
import zipfile
from datetime import datetime

def compress_file(filepath):
    """
    Compress the file using gzip for Linux and zip for Windows.
    Keeps the timestamp from the original file in the compressed file.
    Returns the path to the compressed file.
    """
    original_timestamp = os.path.getmtime(filepath)
    system = platform.system()
    
    if system == "Windows":
        # Use zip compression on Windows.
        zip_path = f"{filepath}.zip"
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            info = zipfile.ZipInfo(os.path.basename(filepath))
            dt = datetime.fromtimestamp(original_timestamp)
            info.date_time = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            with open(filepath, 'rb') as f:
                data = f.read()
            zipf.writestr(info, data)
        return zip_path
    else:
        # Use gzip compression on Linux.
        gz_path = f"{filepath}.gz"
        with open(filepath, 'rb') as f_in, gzip.open(gz_path, 'wb', mtime=original_timestamp) as f_out:
            shutil.copyfileobj(f_in, f_out)
        return gz_path
