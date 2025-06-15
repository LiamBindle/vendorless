# Running Apps


## Commands

The basic commands to interact with an app are `setup` and `run`.
Package developers will also `pkg` to run subcommands to create new packages and development utilities.

Commands come from packages, so you need to know what package the command that command comes from.
The `core` package has all of the basic commands for setting up and running apps, as well as the tools that developers use to create new packages.

The command-line tool `vl` is used to run a `<command>` from a `<package>`.

```
vl <package> <command> <arguments>...
```

The instructions on this page cover how to setup and run an app, using the [Basic Database]() app from the [vendorless.postgres]() package.


---

## Installation

```console
$ git clone git@github.com:LiamBindle/vendorless-postgres.git
$ cd vendorless-postgres
$ poetry install
```

---

## Setting up an App

The `setup` command is used to build the configuration files for an app.
Apps are found in the `apps` submodule of a package.

```
vl core setup vendorless.<package>.apps.<app_name>
```

For our basic database example, the command would be

```console
$ vl core setup vendorless.postgres.stacks.basic_database
```

This command builds the a [Docker Compose]() project for the app.

```tree
./
    vendorless.postgres.stacks.basic_database/
        docker-compose.yaml
```

## Running an App

The `run` command is used to run an app.
This command takes the path to the app's configuration as an argument.
For our basic database example, the command would be 

```console
$ vl core run vendorless.postgres.stacks.basic_database
```

---

Apps come from packages.
You can find premade apps from the [Awesome List of Vendorless Packages](),
or you can write your own apps and blueprints by [Creating a Package]().    