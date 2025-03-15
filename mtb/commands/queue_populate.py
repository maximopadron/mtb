import click
import requests
from mtb.utils.decorators import log_header_footer
from mtb.utils import config_parser, logger
from mtb.utils.zabbix import send_metric

log = logger.get_logger()

def populate_rabbitmq(config):
    mgr = config.get("rabbitmq")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {}
    metrics = {}
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
            messages = q.get("messages", 0)
            key = f"queue.rabbitmq.{mgr_name}.{qname}.messages"
            metrics[key] = messages
    log.info(f"RabbitMQ populate: collected metrics from {len(mgr)} instance(s).")
    return metrics

def populate_kafka(config):
    mgr = config.get("kafka")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {}
    from kafka import KafkaConsumer, TopicPartition
    metrics = {}
    for instance in mgr:
        servers = instance.get("bootstrap_servers", "localhost:9092")
        mgr_name = instance.get("name", "kafka")
        consumer = KafkaConsumer(bootstrap_servers=servers, enable_auto_commit=False)
        topics = consumer.topics()
        for topic in topics:
            partitions = consumer.partitions_for_topic(topic)
            if not partitions:
                continue
            total = 0
            for p in partitions:
                tp = TopicPartition(topic, p)
                consumer.assign([tp])
                consumer.seek_to_end(tp)
                latest = consumer.position(tp)
                consumer.seek_to_beginning(tp)
                earliest = consumer.position(tp)
                total += (latest - earliest)
            key = f"queue.kafka.{mgr_name}.{topic}.messages"
            metrics[key] = total
        consumer.close()
    log.info(f"Kafka populate: collected metrics from {len(mgr)} instance(s).")
    return metrics

def populate_activemq(config):
    mgr = config.get("activemq")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {}
    import re
    metrics = {}
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
                read_url = f"{api_url}/read/{mbean}/QueueSize"
                r = requests.get(read_url, auth=(user, password))
                r.raise_for_status()
                value = r.json().get("value", 0)
                key = f"queue.activemq.{mgr_name}.{qname}.messages"
                metrics[key] = value
    log.info(f"ActiveMQ populate: collected metrics from {len(mgr)} instance(s).")
    return metrics

def populate_ibmmq(config):
    mgr = config.get("ibmmq")
    if mgr:
        if not isinstance(mgr, list):
            mgr = [mgr]
    else:
        return {}
    metrics = {}
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
            messages = q.get("currentDepth", 0)
            key = f"queue.ibmmq.{mgr_name}.{qname}.messages"
            metrics[key] = messages
    log.info(f"IBM MQ populate: collected metrics from {len(mgr)} instance(s).")
    return metrics

@click.command(name="queue-populate", help="Populate Zabbix items with current message counts for all configured queue managers.")
@log_header_footer
def queue_populate():
    config = config_parser.load_config("config.yaml")
    overall = {}
    if config.get("rabbitmq"):
        overall.update(populate_rabbitmq(config))
    if config.get("kafka"):
        overall.update(populate_kafka(config))
    if config.get("activemq"):
        overall.update(populate_activemq(config))
    if config.get("ibmmq"):
        overall.update(populate_ibmmq(config))
    # Send each metric to Zabbix.
    for key, value in overall.items():
        send_metric(key, value)
        click.echo(f"Sent metric {key}: {value}")
        log.info(f"Sent metric {key} = {value}")

if __name__ == '__main__':
    queue_populate()
