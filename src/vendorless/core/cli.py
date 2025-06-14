import importlib
import pkgutil
import click


import pkgutil
import sys
import vendorless

package_cli = {}
for module_info in pkgutil.iter_modules(vendorless.__path__):
    try:
        mod = __import__(f'vendorless.{module_info.name}.commands', fromlist=['cli'])
        cli = getattr(mod, 'cli', None)
        if cli is not None:
            package_cli[module_info.name] = cli
    except ImportError:
        pass


@click.group()
def main():
    """Dispatcher CLI."""


# Dynamically add subcommands to the main group
for name, cmd in package_cli.items():
    main.add_command(cmd, name=name)


if __name__ == "__main__":
    main()