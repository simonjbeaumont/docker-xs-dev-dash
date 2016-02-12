IMG_NAME=ring3-dash
DATA_CON=$(IMG_NAME)-data
PORTS=-p 80:80 -p 3000:3000
VOLUMES=--volumes-from $(DATA_CON)

build: .build-done

.build-done: .
	docker build -t $(IMG_NAME) .
	@docker inspect -f '{{.Id}}' $(IMG_NAME) > .build-done

clean:
	@rm -f .build-done

run: build data
	docker run --rm -ti $(VOLUMES) $(PORTS) $(IMG_NAME)

shell: build
	docker run --rm -ti $(VOLUMES) $(PORTS) $(IMG_NAME) /bin/bash

data: build
	docker run --name=$(DATA_CON) -ti $(IMG_NAME) true

purge:
	@read -n1 -r -p "This will remove all persistent data. Are you sure? " ;\
	echo ;\
	if [ "$$REPLY" == "y" ]; then \
		docker rm -f $(DATA_CON); \
	fi

.PHONY: build clean run shell data purge
