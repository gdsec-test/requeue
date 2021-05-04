from rabbitmq.consumer import Consumer
from rabbitmq.producer import Publisher
import os

user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
host = os.getenv('BROKER_URL')
port = os.getenv('PORT')
vhost = os.getenv('VHOST')

if __name__ == '__main__':
    p = Publisher(host=host, user=user, password=password, port=port, vhost=vhost)
    p.connect()
    c = Consumer(user=user, password=password, host=host, port=port,
                 vhost=vhost, publisher=p)
    c.connect()
    while True:
        c.consume()