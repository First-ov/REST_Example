FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /web_django
WORKDIR /web_django
COPY ./ /web_django/
RUN pip install --upgrade pip && pip install -r requirements.txt