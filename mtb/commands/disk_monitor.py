import click
import psutil
from mtb.utils.decorators import log_header_footer
from mtb.utils.zabbix import send_metric
from mtb.utils import logger

@click.command(name="disk-monitor", help="Monitor disk usage and send metrics to Zabbix.")
@click.option('--partition', default=None, help="Specific partition (mount point) to monitor (optional)")
@log_header_footer
def disk_monitor(partition):
    """
    Monitor disk usage on the system.
    If --partition is provided, only that mount point is checked; otherwise, all partitions are monitored.
    For each partition, the metric key is formatted as: disk.usage[<mountpoint>]
    """
    log = logger.get_logger()
    results = {}
    if partition:
        parts = [p for p in psutil.disk_partitions() if p.mountpoint == partition]
    else:
        parts = psutil.disk_partitions()
    
    for p in parts:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            usage_percent = usage.percent
            key = f"disk.usage[{p.mountpoint}]"
            results[key] = usage_percent
            send_metric(key, usage_percent)
            log.info(f"Sent metric {key} = {usage_percent}")
        except Exception as e:
            log.error(f"Error monitoring partition {p.mountpoint}: {e}")
    
    for k, v in results.items():
        click.echo(f"{k}: {v}")

if __name__ == '__main__':
    disk_monitor()
