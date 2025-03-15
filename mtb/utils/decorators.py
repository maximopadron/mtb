import functools
import click
from datetime import datetime
from mtb.utils import logger

log = logger.get_logger()

def log_header_footer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context(silent=True)
        script_name = ctx.command.name if ctx and ctx.command else func.__name__
        start_time = datetime.now()
        provided_params = ctx.params if ctx else {}
        # Extract default parameters from the command's options.
        default_params = {}
        if ctx and ctx.command:
            for param in ctx.command.params:
                if hasattr(param, 'default'):
                    default_params[param.name] = param.default
        header = {
            "script": script_name,
            "start_time": start_time.isoformat(),
            "provided_parameters": provided_params,
            "default_parameters": default_params,
        }
        # Print header to stdout and log it
        click.echo("--- HEADER ---")
        click.echo(header)
        log.info(f"HEADER: {header}")
        
        exit_code = 0  # Default exit code
        
        try:
            result = func(*args, **kwargs)
            # If the function returns an integer, treat it as the exit code.
            if result is not None and isinstance(result, int):
                exit_code = result
        except Exception:
            exit_code = 1
            raise
        finally:
            end_time = datetime.now()
            footer = {
                "end_time": end_time.isoformat(),
                "exit_code": exit_code
            }
            # Print footer to stdout and log it
            click.echo("--- FOOTER ---")
            click.echo(footer)
            log.info(f"FOOTER: {footer}")
        return result
    return wrapper
