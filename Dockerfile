FROM docker-dcu-local.artifactory.secureserver.net/dcu-python3.11:1.1

WORKDIR /app

USER root
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY main.py /app/
COPY rabbitmq /app/rabbitmq
USER dcu
ENTRYPOINT ["python", "/app/main.py"]