import click
import subprocess
from mtb.utils import logger
from mtb.utils.decorators import log_header_footer

log = logger.get_logger()

@click.command(name="run", help="Execute an external script or executable with parameters.")
@click.argument('-e', '--executable', type=click.Path(exists=True))
@click.argument('-p', '--params', nargs=-1)
@log_header_footer
def run_cmd(executable, params):
    """
    Executes an external executable or script with provided parameters.

    :param executable: Path to the executable or script.
    :param params: Parameters to pass to the executable.
    """
    log.info(f"Running executable: {executable} with parameters: {params}")
    try:
        result = subprocess.run([executable] + list(params), capture_output=True, text=True, check=True)
        click.echo(result.stdout)
        log.info(f"Executable output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        log.error(f"Error executing {executable}: {e.stderr}")
        click.echo(e.stderr)
