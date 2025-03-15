from mtb.utils import config_parser, logger
from zabbix_utils import ZabbixSender  # Make sure zabbix_utils is installed

def send_metric(key, value, host=None):
    """
    Sends a metric to Zabbix using the zabbix_utils library.
    Global configuration is read from config.yaml:
      - zabbix_server: Zabbix server address (default: 127.0.0.1)
      - zabbix_port: Zabbix port (default: 10051)
      - zabbix_host: The host name as registered in Zabbix (default: mtb-host)
    
    :param key: The Zabbix item key (e.g. disk.usage[/])
    :param value: The value to send.
    :param host: Optional; override the host name.
    :return: The result from the Zabbix sender.
    """
    log = logger.get_logger()
    config = config_parser.load_config("config.yaml")
    zabbix_server = config.get("zabbix_server", "127.0.0.1")
    zabbix_port = config.get("zabbix_port", 10051)
    if host is None:
        host = config.get("zabbix_host", "mtb-host")
    
    try:
        sender = ZabbixSender(server=zabbix_server, port=zabbix_port)
        # Assume the send() method accepts a dict with host, key, and value.
        result = sender.send({'host': host, 'key': key, 'value': value})
        log.info(f"Sent metric {key} = {value} to Zabbix, result: {result}")
        return result
    except Exception as e:
        log.error(f"Error sending metric to Zabbix: {e}")
        return None
