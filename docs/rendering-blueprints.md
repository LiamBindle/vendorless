# Rendering Blueprints
A blueprint is a Python module that can be rendered to Docker Compose files that run an application.
We won't get into the details of a blueprint's *.py* file here, but it simply configures *service templates* to stand up all of the services that are needed to run the application.

This page will render a Keycloak authentation server as an example. 
The general workflow is the same for rendering a blueprint other packages.


## Step 1: Install Packages

Install the package that provides the blueprint that you want to render.
```console
$ pip install vendorless-keycloak
```

## Step 2: Render the Blueprint

Run the `vl core render` command to render a blueprint to Docker Compose files.
Generally, vendorless packages provide blueprints at `vendorless.<package>.blueprints.<app_name>` so the command usually has the form: 

```
vl core render -m vendorless.<package>.blueprints.<app_name>
```

For our keycloak authentication server the command would be:

```console
$ vl core render -m vendorless.keycloak.blueprints.auth_server
```

!!! note "Rendering A Blueprint From A Local File"

    You can render blueprints from a local *.py* file like so:

    ```console
    $ vl core render ./path/to/blueprint.py
    ```

Your current working directory should now have a subdirectory with the rendered Docker Compose files.

```text
./
└── vendorless.keycloak.blueprints.auth_server/
    └── docker-compose.yaml
```

## Step 3: Start The Application

Launch the application using Docker Compose.

```console
$ cd vendorless.keycloak.blueprints.auth_server/
$ docker compose up
```