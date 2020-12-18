# RecipeRadar Static Content

This repository hosts a static content site generated from RecipeRadar's knowledge base.

## Install dependencies

Make sure to follow the RecipeRadar [infrastructure](https://www.github.com/openculinary/infrastructure) setup to ensure all cluster dependencies are available in your environment.

## Development

To install development tools and run linting and tests locally, execute the following commands:

```sh
$ make lint tests
```

## Local Deployment

To deploy the service to the local infrastructure environment, execute the following commands:

```sh
$ make
$ make deploy
```
