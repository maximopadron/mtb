import click
import psutil
from mtb.utils.decorators import log_header_footer
from mtb.utils.zabbix import send_metric
from mtb.utils import logger

@click.command(name="process-monitor", help="Monitor peak CPU and RAM usage among processes and send metrics to Zabbix.")
@log_header_footer
def process_monitor():
    """
    Monitors running processes to determine:
      - process.top_cpu: highest CPU usage (%)
      - process.top_mem: highest memory usage (in MB)
    """
    log = logger.get_logger()
    top_cpu = 0.0
    top_mem = 0
    for proc in psutil.process_iter(['cpu_percent', 'memory_info', 'name']):
        try:
            cpu = proc.info['cpu_percent']
            mem = proc.info['memory_info'].rss  # in bytes
            if cpu > top_cpu:
                top_cpu = cpu
            if mem > top_mem:
                top_mem = mem
        except Exception as e:
            log.error(f"Error retrieving process info: {e}")
    
    top_mem_mb = top_mem / (1024 * 1024)
    send_metric("process.top_cpu", top_cpu)
    send_metric("process.top_mem", top_mem_mb)
    click.echo(f"Top CPU usage: {top_cpu}%")
    click.echo(f"Top Memory usage: {top_mem_mb} MB")

if __name__ == '__main__':
    process_monitor()
