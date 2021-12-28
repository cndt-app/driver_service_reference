FROM python:3.9

RUN pip install --no-input --no-cache-dir --disable-pip-version-check poetry && \
    poetry config virtualenvs.create false
WORKDIR /app

ADD poetry.lock pyproject.toml /app/
RUN poetry install --no-dev

EXPOSE 8000
ENTRYPOINT ["uvicorn", "web:app", "--port", "8000", "--host", "0.0.0.0"]

ADD . /app/
