# Pull base image
FROM python:3.8.6

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# install dependencies
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# copy project
COPY ./app /code/app
COPY ./.env /code/.env
COPY ./alembic.ini /code/alembic.ini
COPY ./alembic /code/alembic
COPY ./tests /code/tests

# run the app
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0" , "--reload" , "--port", "8000"]