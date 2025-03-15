import click
import json
import re
import requests
from mtb.utils.decorators import log_header_footer
from mtb.utils import config_parser, logger

log = logger.get_logger()

# Define a constant for the queue macro key
QUEUE_NAME_MACRO = "{#QUEUE_NAME}"

def discover_rabbitmq(config):
    mgr = config.get("rabbitmq")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {"data": []}
    discovery = {"data": []}
    for instance in mgr:
        api_url = instance.get("api_url", "http://localhost:15672/api/queues")
        user = instance.get("user", "guest")
        password = instance.get("password", "guest")
        mgr_name = instance.get("name", "rabbitmq")
        response = requests.get(api_url, auth=(user, password))
        response.raise_for_status()
        queues = response.json()
        for q in queues:
            qname = q.get("name")
            discovery["data"].append({QUEUE_NAME_MACRO: f"{mgr_name}:{qname}"})
    log.info(f"RabbitMQ discovery: found queues from {len(mgr)} instance(s).")
    return discovery

def discover_kafka(config):
    mgr = config.get("kafka")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {"data": []}
    discovery = {"data": []}
    from kafka import KafkaConsumer
    for instance in mgr:
        servers = instance.get("bootstrap_servers", "localhost:9092")
        mgr_name = instance.get("name", "kafka")
        consumer = KafkaConsumer(bootstrap_servers=servers)
        topics = consumer.topics()
        consumer.close()
        for topic in topics:
            discovery["data"].append({QUEUE_NAME_MACRO: f"{mgr_name}:{topic}"})
    log.info(f"Kafka discovery: found topics from {len(mgr)} instance(s).")
    return discovery

def discover_activemq(config):
    mgr = config.get("activemq")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {"data": []}
    discovery = {"data": []}
    for instance in mgr:
        api_url = instance.get("api_url", "http://localhost:8161/api/jolokia")
        user = instance.get("user", "admin")
        password = instance.get("password", "admin")
        mgr_name = instance.get("name", "activemq")
        search_url = f"{api_url}/search/org.apache.activemq:type=Broker,brokerName=*,destinationType=Queue,*"
        response = requests.get(search_url, auth=(user, password))
        response.raise_for_status()
        mbeans = response.json().get("value", [])
        for mbean in mbeans:
            match = re.search(r'destinationName=([^,]+)', mbean)
            if match:
                qname = match.group(1)
                discovery["data"].append({QUEUE_NAME_MACRO: f"{mgr_name}:{qname}"})
    log.info(f"ActiveMQ discovery: found queues from {len(mgr)} instance(s).")
    return discovery

def discover_ibmmq(config):
    mgr = config.get("ibmmq")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {"data": []}
    discovery = {"data": []}
    for instance in mgr:
        base_url = instance.get("api_url", "http://localhost:9443/ibmmq/rest/v1")
        qmgr = instance.get("qmgr", "QM1")
        user = instance.get("user", "")
        password = instance.get("password", "")
        mgr_name = instance.get("name", "ibmmq")
        url = f"{base_url}/admin/monitor/qmgr/{qmgr}/queue?view=basic"
        response = requests.get(url, auth=(user, password))
        response.raise_for_status()
        data = response.json()
        queues = data.get("queues", [])
        for q in queues:
            qname = q.get("name")
            discovery["data"].append({QUEUE_NAME_MACRO: f"{mgr_name}:{qname}"})
    log.info(f"IBM MQ discovery: found queues from {len(mgr)} instance(s).")
    return discovery

@click.command(name="queue-discovery", help="Discover queues for all configured queue managers and output LLD JSON for Zabbix.")
@log_header_footer
def queue_discovery():
    config = config_parser.load_config("config.yaml")
    overall = {"data": []}
    if config.get("rabbitmq"):
        overall["data"].extend(discover_rabbitmq(config)["data"])
    if config.get("kafka"):
        overall["data"].extend(discover_kafka(config)["data"])
    if config.get("activemq"):
        overall["data"].extend(discover_activemq(config)["data"])
    if config.get("ibmmq"):
        overall["data"].extend(discover_ibmmq(config)["data"])
    click.echo(json.dumps(overall, indent=4))

if __name__ == '__main__':
    queue_discovery()
