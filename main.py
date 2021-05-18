import logging
import os

from pika.exceptions import ChannelWrongStateError

from rabbitmq.consumer import Consumer
from rabbitmq.producer import Publisher

user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
host = os.getenv('BROKER_URL')
port = os.getenv('PORT')
vhost = os.getenv('VHOST')
env = os.getenv('sysenv')

if __name__ == '__main__':
    p = Publisher(host=host, user=user, password=password, port=port, vhost=vhost, env=env)
    p.connect()
    c = Consumer(user=user, password=password, host=host, port=port,
                 vhost=vhost, publisher=p, env=env)
    c.connect()
    while True:
        try:
            c.consume()
        except ChannelWrongStateError as cc:
            logging.debug(f'Channel has closed stopping consumer: {cc}')
            exit(0)
