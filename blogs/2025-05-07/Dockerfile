# syntax=docker/dockerfile:1
FROM python:3.13.3-alpine3.21@sha256:18159b2be11db91f84b8f8f655cd860f805dbd9e49a583ddaac8ab39bf4fe1a7 as base

FROM base as example
COPY example.py example.py
ENTRYPOINT ["python3", "example.py"]

FROM base as tests
COPY test-requirements.txt test-requirements.txt
RUN pip install -r test-requirements.txt
COPY tests.py tests.py
ENTRYPOINT ["pytest", "tests.py"]