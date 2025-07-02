
![Logo](assets/full.png)

Vendorless is a Python-based templating engine for rendering Docker Compose projects.
In vendorless, *blueprints* are Python modules that configures the services that make up an application, like databases and servers. 
A blueprint can be rendered to Docker Compose files that run an instance of the application. 
The basic functionality of vendorless is provided by the `vendorless.core` package, and other packages provide specific service templates and blueprints. For example, the `vendorless.postgres` package provides service templates for running a PostGreSQL database, and the `vendorless.keycloak` package provides a blueprint for running a Keycloak authentication server (which uses service templates provided by `vendorless.postgres`).

The goal of vendorless is to make it easier to build your application's backbone using free and open-source services. 
Vendorless is designed for small- to medium-sized projects that value **self-containment** over infinite scalability, and **pragmatic tooling** that prioritizes development efficency, and maintainability. 

## Key Features

1. **Python-based** infrastructure-as-code (IaC). Blueprints are Python modules, which allows of the use of complex scriping, looping, and logic to configure *service templates*.  
2. **Parameter linking** allows the outputs of one *service template* to be linked to the inputs of other service templates. *Service templates* are effectively black boxes that are configured via their input parameters. Service templates also have output parameters, and these output parameters (e.g., ports, URLs, file paths, service names) can be linked to the input parameters of other service templates.
3. **Extensibility** is provided by namespace packaging. Vendorless packages provide service templates (for use in blueprints), CLI commands (e.g., key generation), and/or blueprints (ready-made applications). You can leverage community maintained packages, or [create your own](creating-packages). 


## Commands

`vl` is an extensible command-line tool that runs commands from vendorless packages. The functionality for working with vendorless blueprints and packages is provided by `vendorless.core` which includes:

1. Rendering blueprints
2. Developing new vendorless packages (creating, documenting, testing, and publishing)

Vendorless packages may add additional commands that are related to the package's services (e.g., key generation, certificate generation, secret generation, etc.).

The format of `vl` commands is

```
vl <package> <command> <arguments>...
```

where `<package>` is the vendorless package (e.g., `core`) that provides `<command>`. For example:

```console
$ vl core render -m vendorless.keycloak.blueprints.auth_server
```

You can always use `--help` to see command documentation.

## Commands via Docker

You can run vendorless commands via docker like so:

```
docker run ghcr.io/liambindle/vendorless:latest \
    vendorless.<packages>... \
    <package> <command> <arguments>...
```

This is useful if you're running vendorless in an environment that doesn't have Python (e.g., a production server). The first set of arguments (packages prefixed with `vendorless.`) is the list of vendorless packages that need to be installed. The subsequent arguments are the arguments to the `vl` command. For example

```console
$ docker run ghcr.io/liambindle/vendorless:latest \
    vendorless.core vendorless.keycloak \
    core render -m vendorless.keycloak.blueprints.auth_server
```
