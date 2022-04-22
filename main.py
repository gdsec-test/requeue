import logging
import os

from pika.exceptions import ChannelWrongStateError

from rabbitmq.consumer import Consumer
from rabbitmq.producer import Publisher

single_url = os.getenv('SINGLE_BROKER')
multi_url = os.getenv('MULTIPLE_BROKERS')
queue_type = os.getenv('QUEUE_TYPE')

url = single_url
if queue_type == 'quorum':
    url = multi_url

env = os.getenv('sysenv')

if __name__ == '__main__':
    p = Publisher(url, env)
    c = Consumer(url, p, env)
    while True:
        try:
            c.consume()
        except ChannelWrongStateError as cc:
            logging.debug(f'Channel has closed stopping consumer: {cc}')
            exit(0)
