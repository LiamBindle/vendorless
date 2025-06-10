import importlib
import pkgutil
import click


import pkgutil
import sys

package_cli = {}

import vendorless
for module_info in pkgutil.iter_modules(vendorless.__path__):
    try:
        package_cli[module_info.name] = __import__(f'vendorless.{module_info.name}.commands', fromlist=['cli'])
    except ImportError:
        pass

@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option("-p", '--package', default="core", type=click.Choice(sorted(package_cli.keys())), help="The package that you want to run commands from.")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def main(package, args):
    """Dispatcher CLI."""
    group = getattr(package_cli.get(package, {}), 'cli', None)
    if not group:
        click.echo(f"Plugin '{package}' not found.", err=True)
        raise SystemExit(1)

    group.main(args=args, standalone_mode=False)


if __name__ == "__main__":
    main()