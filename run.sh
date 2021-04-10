#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t debt-scraper .
docker run \
  -it \
  -e DEBTS_URL=$1 \
  -e PAYMENT_PLANS_URL=$2 \
  -e PAYMENTS_URL=$3 \
  --rm debt-scraper python main.py
