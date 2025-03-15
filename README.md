# mtb

A Python 3 toolbox for application support teams. It provides:

- A dynamic command list with descriptions.
- A file watcher to monitor file creation/deletion events with customizable parameters.
- A purge function to delete and then compress old files.
- A backup tool to archive files with modular backup engines (TSM, ScalityS3, Veeam, Rubrik).

All commands log in JSON format (ideal for ELK integration) and are configurable via a global configuration file.

## Installation

```bash
pip install .
