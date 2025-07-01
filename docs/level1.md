# Rendering Blueprints

Below is an example of setting up a Keycloak authentication server.
The `vendorless.keycloak` package provides an authentication server blueprint that we will render to Docker Compose files, which we will then run. The general workflow is the same for rendering a blueprint from a different package.   


First, install the package that provides the blueprint.

```console
$ pip install vendorless-keycloak
```

Next, run the `vl core render` command to render a blueprint.

```
vl core render -m vendorless.<package>.blueprints.<app_name>
```

For our keycloak authentication server the command would be

```console
$ vl core render -m vendorless.keycloak.blueprints.authentication_server
```

Now you should notice the Docker Compose files in a subdirectory.

```
.
└── vendorless.keycloak.blueprints.auth_server/
    └── docker-compose.yaml
```

Now you can run the app using `docker-compose`.

```console
$ cd vendorless.keycloak.blueprints.auth_server/
$ docker compose up
```