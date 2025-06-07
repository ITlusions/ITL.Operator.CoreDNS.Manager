FROM python:3.11-slim

RUN pip install kopf kubernetes

COPY operator /app/operator

WORKDIR /app

CMD ["kopf", "run", "operator/main.py", "--standalone"]
