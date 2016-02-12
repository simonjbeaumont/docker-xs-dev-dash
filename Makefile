IMG_NAME=ring3-dash

build: .build-done

.build-done: .
	docker build -t $(IMG_NAME) .
	@docker inspect -f '{{.Id}}' $(IMG_NAME) > .build-done

clean:
	@rm -f .build-done

run: build
	docker run --rm -ti -p 80:80 -p 3000:3000 $(IMG_NAME)

shell: build
	docker run --rm -ti -p 80:80 -p 3000:3000 $(IMG_NAME) /bin/bash

.PHONY: build clean run shell
