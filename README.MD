
![Logo](assets/full.png)

Vendorless is a Python-based templating engine for rendering Docker Compose projects.
Vendorless introduces the concept of blueprints, which are a Python module that configures all of the services, like databases and servers, that are the backbone of an application.
The Docker Compose for an application are rendered from the application's blueprint.

The basic functionality of vendorless is provided by the `vendorless.core` package, and other packages provide specific service templates and blueprints. For example, the `vendorless.postgres` package provides service templates for running a PostGreSQL database, and the `vendorless.keycloak` package provides a blueprint for running a Keycloak authentication server (which uses service templates provided by `vendorless.postgres`).

The goal of vendorless is to make it easier to build your application's backbone using free and open-source services. 
Vendorless is designed for small- to medium-sized projects that value **self-containment** over infinite scalability, and **pragmatic tooling** that prioritizes development efficency, and maintainability. 

## Key Features

1. **Python-based** infrastructure-as-code (IaC). Blueprints are Python modules, which allows of the use of complex scriping, looping, and logic in the provisioning of services.  
2. **Parameter liking** allows the outputs of one service to be linked to the inputs of another services. Service templates are effectively black boxes with input parameters and output parameters that can be linked to the parameters of other services (e.g., ports, URLs, file paths, environment variables).
3. **Extensibility** is provided by namespace packaging. Vendorless package provide service templates (for use in blueprints), commands (e.g., key generation), and/or blueprints (ready-made applications). You can leverage community maintained packages, or create your own. 
