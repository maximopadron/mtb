import click
from mtb.utils.decorators import log_header_footer

@click.command(name="list", help="List all available functionalities with descriptions.")
@log_header_footer
def list_cmd():
    """
    Dynamically list all available functionalities.
    This command inspects the available subcommands in the CLI and prints their help texts.
    """
    from mtb.mtb.mtb import main

    click.echo("Available functionalities:")
    for command in main.commands:
        cmd = main.commands[command]
        click.echo(f"- {command}: {cmd.help}")

    # Log the listing action
    from mtb.utils import logger
    log = logger.get_logger()
    log.info("Listed all functionalities in mtb")
