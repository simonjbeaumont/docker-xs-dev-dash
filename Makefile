IMG_NAME=ring3-dash
DATA_CON=$(IMG_NAME)-data
PORTS=-p 80:80 -p 3000:3000
VOLUMES=--volumes-from $(DATA_CON)
DEV_VOL=-v $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))):/host

build: .
	docker build -t $(IMG_NAME) .

clean:
	docker rmi $(IMG_NAME)

run: build data
	docker run --rm -ti $(VOLUMES) $(PORTS) $(IMG_NAME)

shell: build data
	docker run --rm -ti $(VOLUMES) $(PORTS) $(DEV_VOL) $(IMG_NAME) /bin/bash

data: build
	docker run --name=$(DATA_CON) -ti $(IMG_NAME) true || true

purge:
	@read -n1 -r -p "This will remove all persistent data. Are you sure? " ;\
	echo ;\
	if [ "$$REPLY" == "y" ]; then \
		docker rm -f $(DATA_CON); \
	fi

.PHONY: build clean run shell data purge
