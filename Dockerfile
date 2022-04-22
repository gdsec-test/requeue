FROM python:3.7

WORKDIR /app

# install custom root certificates
RUN mkdir -p /usr/local/share/ca-certificates/
COPY certs/*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY main.py /app/
COPY rabbitmq /app/rabbitmq
ENTRYPOINT ["python", "/app/main.py"]