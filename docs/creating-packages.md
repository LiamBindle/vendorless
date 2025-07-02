# Creating Packages

Packages can provide blueprints, service templates, and/or commands.
This page will demonstrate creating a vendorless package for a PostGreSQL database.
This is a simple example that will demonstrate the general workflow.


## Setup
The command `vl core package new` is used to create a new package.
The command will prompt you for some basic information about the package that you are creating.
The package will be preconfigured with the right structure, documentation, tests, and GitHub actions for CI. 
If you have installed `vendorless.core` via `pip` you can run the `vl` command directly, or you can run it via docker.

```console
$ docker run ghcr.io/liambindle/vendorless:latest \
    vendorless.core \
    core package new
name:               postgres
version:
description:        PostgreSQL database
author:             Liam Bindle
email:              liam.bindle@gmail.com
github_username:    LiamBindle
license:      
```

Then you can run `poetry install` to install your newly created package.

```console
$ cd vendorless.postgres
$ poetry install
```

## Blueprints
A blueprint is the Python module (*.py* file) that is used by `vl core render` to render the Docker Compose files that stand up and application. Blueprints should go in `vendorless.<package>.blueprints` where `<package>` is the your package.


```python
# vendorless.postgres.blueprints.basic_database

from vendorless.postgres import PostGreSQLDatabase
from vendorless.core import Volume

volume = Volume(
    ...
)

pg_databasn = PostGreSQLDatabase(
    ...
)
```

## Service Templates

Service templates are black boxes that are configure services.
They are effectively black boxes with input parameters that configure the service, and output parameters that can linked to the inputs of other service templates.
This parameter linking is useful to ensure that things like ports, urls, service names, etc. are connected properly between services.

You can put service templates anywhere, but your top-level `__init__.py` file should import all of the service templates that your package provides. Below is an example of creating a service template for a PostGreSQL database in a file called *service_templates.py*.

```python
# vendorless.postgres.service_templates.py

from dataclasses import dataclass
from vendorless.core import Blueprint, parameter, computed_parameter, Volume

@dataclass
class PostGreSQLDatabase(Blueprint):
    volume_name: str = parameter()             # required because no default
    data_path: str = parameter()

    username: str =  parameter("admin")        # default is "admin"
    password: str = parameter("admin")
    service_name: str = parameter("postgres")  # default is "postgres"
    database_name: str = parameter("pgdata")   # detault is "pgdata"

    @computed_parameter
    def port(self) -> int:  # used to evaluate parameters lazily
        return 5432
```

Then in the top-level `__init__.py` file we would have

```python
# vendorless.postgres.__init__.py
from .service_templates import PostGreSQLDatabase
```

This way, dependent packages have nicely formatted import statements like so:

```python
from vendorless.postgres import PostGreSQLDatabase
``` 



## Commands
The `vl` command-line tool uses [Click](https://click.palletsprojects.com/en/stable/). If you want to add any commands to your package, you should implement them in `vendorless.<package>.commands.py` using `@cli.group()`. For example:

```python
# vendorless.<package>.commands.py

# (...)

@cli.group()
@click.argument('message', type=click.STRING)
def echo(message: str):
    click.echo(message)

```
