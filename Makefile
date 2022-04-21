SHELL := /bin/bash

.PHONY: image run clean
.DEFAULT: all

image:
	docker build . -t dm-checker

clean:
	docker rmi $(docker images -f "dangling=true" -q)

run:
	docker run --rm -it dm-checker bash

all: image run
