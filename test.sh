#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t debt-scraper .
docker run \
  -it \
  --rm debt-scraper python -m unittest -v
