import logging
import os

from elasticapm import Client, instrument
from pika.exceptions import ChannelWrongStateError

from rabbitmq.consumer import Consumer
from rabbitmq.producer import Publisher

multi_url = os.getenv('MULTIPLE_BROKERS')

url = multi_url

env = os.getenv('sysenv')

instrument()
apm = Client(service_name='requeue')


if __name__ == '__main__':
    p = Publisher(url, env)
    c = Consumer(url, p, env)
    while True:
        apm.begin_transaction(transaction_type='event')
        try:
            c.consume()
        except ChannelWrongStateError as cc:
            logging.debug(f'Channel has closed stopping consumer: {cc}')
            exit(0)
        apm.end_transaction(name="consume queue", result="success")
