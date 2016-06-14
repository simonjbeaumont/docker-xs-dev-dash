IMG_NAME=ring3-dash
DATA_CON=$(IMG_NAME)-data
DASH_CON=$(IMG_NAME)
PORTS+=-p 80:80
VOLUMES+=--volumes-from $(DATA_CON) -v /etc/localtime:/etc/localtime:ro
DEV_VOL=-v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/host

build: . scripts/.gh-token
	docker build -t $(IMG_NAME) .

clean:
	docker rmi $(IMG_NAME) 2>/dev/null || true
	[ ! -s .gh-token ] && rm -f .gh-token

stop:
	docker rm -f $(DASH_CON) 2>/dev/null || true

run: build data stop
	docker run --name=$(DASH_CON) -d -ti $(VOLUMES) $(PORTS) $(IMG_NAME)

shell: build data stop
	docker run --name=$(DASH_CON) --rm -ti $(VOLUMES) $(PORTS) $(DEV_VOL) $(IMG_NAME) /bin/bash

data: build
	docker run --name=$(DATA_CON) -ti $(IMG_NAME) true 2>/dev/null || true

purge: stop
	@read -n1 -r -p "This will remove all persistent data. Are you sure? " ;\
	echo ;\
	if [ "$$REPLY" == "y" ]; then \
		docker rm -f $(DATA_CON) 2>/dev/null || true; \
	fi

check: build
	docker run --rm -it $(DEV_VOL) $(IMG_NAME) bash -c "cd /host; pep8 --show-source --show-pep8 /host/scripts/*.py"
	docker run --rm -it $(DEV_VOL) $(IMG_NAME) bash -c "cd /host; pylint scripts/*.py"
	docker run --rm -it $(DEV_VOL) $(IMG_NAME) jsonlint /host/grafana/dash.json

scripts/.gh-token:
	@if [ ! -s $@ ]; then \
		read -n1 -r -p "$@ does not exist, create dummy token? "; echo; \
		if [ "$$REPLY" != "y" ]; then \
			echo "Aborting"; \
			exit 2; \
		fi \
	fi
	@touch $@

.PHONY: build clean stop run shell data purge check
