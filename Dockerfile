FROM python:3.9

WORKDIR /app

RUN pip install --no-cache-dir --disable-pip-version-check poetry==1.2.* && \
     poetry config virtualenvs.create false
ADD poetry.lock pyproject.toml /app/
RUN poetry install --no-dev

EXPOSE 8000
ENTRYPOINT ["uvicorn", "src.web:app", "--port", "8090", "--host", "0.0.0.0"]

ADD . /app/
