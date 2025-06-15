# Creating Packages

Packages can provide apps, commands, and blueprints.
An app is the Python module (.py) that `vl core setup` executes before it renders the docker compose project for the app.
App modules use blueprints to compose the services and resources that host the app.
A blueprint is Python objects that represent a piece of infrastructure like a service or a host.
Blueprints are essentially infrastructure black boxes with input parameters and output parameters.
Blueprint parameters can be linked together, allowing for input parameters from one blueprint to be linked to the output parameter of a different blueprint, so that updates propagate to dependencies automatically.

Some packages provide commands too.
These commands are utilities that accompany the apps in a package.
Examples of commands from packages might include commands for generating self-signed certificates, or creating a new user.

The instructions on this page cover how to create a package with blueprints and apps. These instructions will demonstrate creating the [vendorless.postgres]() package.

---

## Installation

```console
$ docker run ghcr.io/liambindle/vendorless:latest \
    vendorless.core \
    core pkg new
$ poetry install
```

---

## Create a New Package

The `pkg new` command is used to create a new package. 
The command will prompt you for some basic information about the package, before it creates the Python package.
The documentation for your new vendorless package can be served live by running `vl core pkg docs-serve`.
Out of the box, the package includes CI actions to deploy the documentation to GitHub Pages, run tests with pytest, and deploy releases to PyPI.

```console
$ vl core pkg new
```

```salt
name:               postgres
version:
description:        PostgreSQL database
author:             Liam Bindle
email:              liam.bindle@gmail.com
github_username:    LiamBindle
license:            
```

## Writing Apps

```python
# vendorless.postgres.apps.basic_database

from vendorless.postgres.blueprints import PostGreSQLDatabase
from vendorless.core.blueprints import Volume

volume = Volume(
    ...
)

pg_databasn = PostGreSQLDatabase(
    ...
)
```

See [Running Apps]() for instructions on how to setup and run the app's module.

## Writing Blueprints

```python
# vendorless.postgres.blueprints

from dataclasses import dataclass
from vendorless.core.base import Blueprint, parameter, computed_parameter
from vendorless.core.blueprints import Volume

@dataclass
class PostGreSQLDatabase(Blueprint):
    volume_name: str = parameter()             # required because no default
    data_path: str = parameter()

    username: str =  parameter("admin")        # default is "admin"
    password: str = parameter("admin")
    service_name: str = parameter("postgres")
    database_name: str = parameter("pgdata")

    @computed_parameter
    def port(self) -> int:  # used to compute parameters lazily
        return 5432
```

---

## Writing Documentation

```console
$ vl core pkg docs-serve
```

## Publishing

```console
$ vl core pkg publish
```
