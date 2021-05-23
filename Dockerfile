# https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

# set environment variables
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# set working directory
WORKDIR /code

# copy project
COPY . /code/

# install dependencies
RUN pip install -r requirements.txt

# expose port
EXPOSE 8000

# Run server
ENTRYPOINT make server