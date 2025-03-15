import click
import json
from mtb.utils.decorators import log_header_footer
from mtb.utils import config_parser, logger

log = logger.get_logger()

@click.command(name="logfile-monitor", help="Generate LLD JSON for log files defined in logs.yaml using native Zabbix keys for age and pattern.")
@log_header_footer
def logfile_monitor():
    """
    Reads configuration from logs.yaml, where each key is a log file path and its value may contain:
      - age: a threshold (e.g. "1h")
      - patterns: a list of regex patterns

    The script does not calculate the file age or search for patterns—it simply outputs a discovery JSON with macros:
      - {#FILE}: The log file path.
      - {#AGE_THRESHOLD}: The age threshold (if defined).
      - {#PATTERNS}: Semicolon-separated regex patterns (if defined).

    You can then create native Zabbix items using keys such as:
      - vfs.file.time[{#FILE}] for file age.
      - log[{#FILE}, {#PATTERN}] for log monitoring.
    """
    logs_config = config_parser.load_config("logs.yaml")
    if not logs_config:
        click.echo("No configuration found in logs.yaml", err=True)
        return 1

    discovery = {"data": []}
    for file_path, settings in logs_config.items():
        entry = {"{#FILE}": file_path}
        if "age" in settings:
            entry["{#AGE_THRESHOLD}"] = str(settings["age"])
        if "patterns" in settings:
            patterns = settings["patterns"]
            if not isinstance(patterns, list):
                patterns = [patterns]
            # Join multiple patterns into a single string separated by semicolon.
            entry["{#PATTERNS}"] = ";".join(patterns)
        discovery["data"].append(entry)

    click.echo(json.dumps(discovery, indent=4))

if __name__ == '__main__':
    logfile_monitor()
