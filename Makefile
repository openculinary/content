.PHONY: build lint tests

SERVICE=$(shell basename $(shell git rev-parse --show-toplevel))
REGISTRY=registry.openculinary.org
PROJECT=reciperadar

IMAGE_NAME=${REGISTRY}/${PROJECT}/${SERVICE}
IMAGE_COMMIT := $(shell git rev-parse --short HEAD)
IMAGE_TAG := $(strip $(if $(shell git status --porcelain --untracked-files=no), latest, ${IMAGE_COMMIT}))

build-dev: image-create render-content image-finalize

build: lint tests image-create render-content image-finalize

deploy:
	kubectl apply -f k8s
	kubectl set image deployments -l app=${SERVICE} ${SERVICE}=${IMAGE_NAME}:${IMAGE_TAG}

image-create:
	$(eval container=$(shell buildah from docker.io/library/nginx:alpine))
	buildah copy $(container) 'etc/nginx/conf.d' '/etc/nginx/conf.d'
	buildah run $(container) -- rm -rf /usr/share/nginx/html --

image-finalize:
	buildah copy $(container) 'public' '/usr/share/nginx/html'
	buildah config --port 80 --entrypoint '/usr/sbin/nginx -g "daemon off;"' $(container)
	buildah commit --squash --rm $(container) ${IMAGE_NAME}:${IMAGE_TAG}

lint:
	pipenv run flake8

tests:
	pipenv run pytest tests

render-content:
	rm -rf public
	pipenv run python -m web.app
