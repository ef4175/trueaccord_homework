FROM python:3.9.4

WORKDIR /app

COPY main.py .
COPY helpers.py .
COPY unit_tests unit_tests
