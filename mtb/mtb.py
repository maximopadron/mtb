import click
import importlib
import pkgutil
from mtb.utils import config_parser, logger

log = logger.get_logger()

@click.group()
def main():
    """
    mtb: Maximus Toolbox is a set of tools for application support.
    """
    pass

def load_commands():
    """
    Dynamically load all commands from the mtb.commands package.
    Any attribute in a module that is a Click Command instance will be registered.
    """
    import mtb.commands
    package = mtb.commands
    package_path = package.__path__
    commands_pkg = package.__name__

    for _, module_name, _ in pkgutil.iter_modules(package_path):
        module = importlib.import_module(f"{commands_pkg}.{module_name}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, click.core.Command):
                main.add_command(attr)
                log.info(f"Loaded command: {attr.name} from module {module_name}")

load_commands()

if __name__ == "__main__":
    config = config_parser.load_config("config.yaml")
    main()
