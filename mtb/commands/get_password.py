import click
from mtb.utils.decorators import log_header_footer
from mtb.utils import config_parser, logger

try:
    import pyaim
except ImportError:
    pyaim = None
try:
    import conjur
except ImportError:
    conjur = None

def _handle_error(message):
    log = logger.get_logger()
    click.echo(message, err=True)
    log.error(message)
    return 1

def _get_password_pyaim(safe, object_name, folder, config):
    log = logger.get_logger()
    req_keys = ["cyberark_endpoint", "cyberark_user", "cyberark_password"]
    if not all(config.get(key) for key in req_keys):
        return _handle_error("Missing CyberArk configuration for pyaim")
    try:
        pyaim.initialize(
            endpoint=config.get("cyberark_endpoint"),
            user=config.get("cyberark_user"),
            password=config.get("cyberark_password")
        )
        log.info("Initialized pyaim client")
        return pyaim.get_password(safe=safe, object_name=object_name, folder=folder)
    except Exception as e:
        return _handle_error(f"Error retrieving password via pyaim: {e}")

def _get_password_conjur(safe, object_name, folder, config):
    log = logger.get_logger()
    req_keys = ["conjur_url", "conjur_account", "conjur_apikey"]
    if not all(config.get(key) for key in req_keys):
        return _handle_error("Missing Conjur configuration")
    try:
        conjur.initialize(
            url=config.get("conjur_url"),
            account=config.get("conjur_account"),
            api_key=config.get("conjur_apikey")
        )
        log.info("Initialized Conjur client")
        return conjur.get_password(safe=safe, object_name=object_name, folder=folder)
    except Exception as e:
        return _handle_error(f"Error retrieving password via conjur: {e}")

@click.command(name="get-password", help="Retrieve a password from a CyberArk safe using pyaim or conjur.")
@click.option('-m', '--method', type=click.Choice(['pyaim', 'conjur'], case_sensitive=False), default='pyaim',
              help="Method to use for retrieving password (pyaim or conjur)")
@click.option('-s', '--safe', required=True, help="Name of the safe")
@click.option('-o', '--object', 'object_name', required=True, help="Name of the object (secret) in the safe")
@click.option('-f', '--folder', default="", help="Optional folder within the safe")
@log_header_footer
def get_password(method, safe, object_name, folder):
    """
    Retrieve a password from a CyberArk safe using the specified method.
    
    For method "pyaim":
      - Requires: cyberark_endpoint, cyberark_user, cyberark_password in config.
      - Uses pyaim to initialize and retrieve the password.
    
    For method "conjur":
      - Requires: conjur_url, conjur_account, conjur_apikey in config.
      - Uses conjur to initialize and retrieve the password.
    """
    log = logger.get_logger()
    config = config_parser.load_config("config.yaml")
    method = method.lower()

    if method == 'pyaim':
        retrieved_password = _get_password_pyaim(safe, object_name, folder, config)
    elif method == 'conjur':
        retrieved_password = _get_password_conjur(safe, object_name, folder, config)
    else:
        return _handle_error("Unsupported method provided.")

    if isinstance(retrieved_password, int):
        # An error occurred and _handle_error returned 1.
        return retrieved_password

    if retrieved_password:
        click.echo(f"Retrieved password: {retrieved_password}")
        log.info("Password retrieved successfully")
    else:
        return _handle_error("No password retrieved")

if __name__ == '__main__':
    get_password()
