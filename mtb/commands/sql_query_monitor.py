import os
import threading
import time
import click
import sqlite3
from mtb.utils.decorators import log_header_footer
from mtb.utils import config_parser, logger
from mtb.utils.time_utils import parse_interval
from mtb.utils.zabbix import send_metric

# Optional DB connectors
try:
    import mysql.connector
except ImportError:
    mysql = None
try:
    import cx_Oracle
except ImportError:
    cx_Oracle = None
try:
    import pyodbc
except ImportError:
    pyodbc = None

log = logger.get_logger()

def get_db_connection(item):
    """
    Return a database connection using parameters from the item.
    Supported types: sqlite, mysql, oracle, sqlserver.
    """
    db_type = item.get("db_type", "sqlite").lower()
    
    if db_type == "sqlite":
        db_file = item.get("db_conn")
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"SQLite file '{db_file}' does not exist.")
        return sqlite3.connect(db_file)
    
    elif db_type == "mysql":
        if mysql is None:
            raise ImportError("mysql.connector is not installed.")
        return mysql.connector.connect(
            host=item.get("db_host", "localhost"),
            port=item.get("db_port", 3306),
            database=item.get("db_conn"),
            user=item.get("db_user"),
            password=item.get("db_passswd")
        )
    
    elif db_type == "oracle":
        if cx_Oracle is None:
            raise ImportError("cx_Oracle is not installed.")
        dsn = item.get("db_conn")
        return cx_Oracle.connect(item.get("db_user"), item.get("db_passswd"), dsn)
    
    elif db_type == "sqlserver":
        if pyodbc is None:
            raise ImportError("pyodbc is not installed.")
        server = item.get("db_host", "localhost")
        database = item.get("db_conn")
        user = item.get("db_user")
        password = item.get("db_passswd")
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={user};PWD={password}"
        return pyodbc.connect(conn_str)
    
    else:
        raise ValueError(f"Unsupported db_type: {db_type}")

def process_item(item_name, item):
    """
    Executes the SQL query defined in item, sends the first column of the first row
    to Zabbix using the metric key sql.<item_name>, and logs/prints the result.
    """
    log.info(f"Processing {item_name}")
    try:
        conn = get_db_connection(item)
        cursor = conn.cursor()
        query = item.get("query")
        if not query:
            log.error(f"No query defined for {item_name}")
            return
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        value = result[0] if result is not None else None
        if value is not None:
            metric_key = f"sql.{item_name}"
            send_metric(metric_key, value)
            click.echo(f"Sent metric {metric_key}: {value}")
            log.info(f"{item_name} query result: {value}")
        else:
            log.error(f"{item_name}: Query returned no result.")
            click.echo(f"{item_name}: Query returned no result.", err=True)
    except Exception as e:
        log.error(f"Error processing {item_name}: {e}")
        click.echo(f"Error processing {item_name}: {e}", err=True)

def run_recurrent(item_name, item, interval_sec):
    """
    Runs process_item() for a given item in an infinite loop with sleep interval_sec between runs.
    """
    while True:
        process_item(item_name, item)
        time.sleep(interval_sec)

@click.command(name="sql-query-monitor", help="Execute SQL queries from a YAML config and send results to Zabbix repeatedly if specified.")
@log_header_footer
def sql_config_monitor(config_file):
    """
    Reads a SQL configuration YAML file containing multiple items.
    
    For each item (e.g. item_name1), the file should define:
      - db_type: The type of the database (sqlite, mysql, oracle, sqlserver)
      - db_conn: For sqlite, the file path; for others, the database name/DSN.
      - db_user: Database username.
      - db_passswd: Database password.
      - query: The SQL query to execute.
      - recurrent: (optional) A string representing the interval (e.g., "1h", "30m") at which to repeat the query.
    
    The script executes each query and sends the first column of the first row to Zabbix 
    with a metric key formatted as: sql.<item_name>
    
    If recurrent is provided, the query is executed repeatedly on that interval.
    """
    sql_config_data = config_parser.load_config("sql_query.yaml")
    threads = []
    
    for item_name, item in sql_config_data.items():
        recurrent = item.get("recurrent")
        if recurrent:
            interval_sec = parse_interval(str(recurrent))
            if interval_sec is None:
                click.echo(f"Invalid recurrent value for {item_name}. Skipping recurrent execution.", err=True)
                process_item(item_name, item)
            else:
                t = threading.Thread(target=run_recurrent, args=(item_name, item, interval_sec), daemon=True)
                t.start()
                threads.append(t)
                click.echo(f"Started recurrent execution for {item_name} every {interval_sec} seconds.")
        else:
            process_item(item_name, item)
    
    # If any recurrent threads were started, keep the main thread alive.
    if threads:
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            click.echo("Exiting due to keyboard interrupt.")
            log.info("Exiting recurrent loops due to keyboard interrupt.")

if __name__ == '__main__':
    sql_config_monitor()
