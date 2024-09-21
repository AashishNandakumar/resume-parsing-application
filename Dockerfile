FROM python:3.10.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN apt-get update && apt-get install redis-server -y
RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader words
RUN python -m nltk.downloader stopwords


COPY . /app/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]
