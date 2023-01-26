# Pull base image
FROM python:3.6.8

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code/

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .