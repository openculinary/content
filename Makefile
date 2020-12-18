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
	buildah config --port 80 --cmd '/usr/sbin/nginx -g "daemon off;"' $(container)
	buildah commit --quiet --rm --squash $(container) ${IMAGE_NAME}:${IMAGE_TAG}

# Virtualenv Makefile pattern derived from https://github.com/bottlepy/bottle/
venv: venv/.installed requirements.txt requirements-dev.txt
	venv/bin/pip install --requirement requirements-dev.txt
	touch venv
venv/.installed:
	python3 -m venv venv
	venv/bin/pip install pip-tools
	touch venv/.installed

requirements.txt: requirements.in
	venv/bin/pip-compile --allow-unsafe --generate-hashes --no-header requirements.in

requirements-dev.txt: requirements-dev.in
	venv/bin/pip-compile --allow-unsafe --generate-hashes --no-header requirements-dev.in

lint: venv
	venv/bin/flake8 tests
	venv/bin/flake8 web

tests: venv
	venv/bin/pytest tests

render-content: venv
	rm -rf public
	venv/bin/python -m web.app
