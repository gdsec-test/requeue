import logging
import os

from elasticapm import (Client, instrument, register_exception_tracking,
                        register_instrumentation)
from pika.exceptions import ChannelWrongStateError

from rabbitmq.consumer import Consumer
from rabbitmq.producer import Publisher

multi_url = os.getenv('MULTIPLE_BROKERS')

url = multi_url

env = os.getenv('sysenv')
instrument()
apm_client = Client(service_name='requeue', env=env)
register_exception_tracking(apm_client)
register_instrumentation(apm_client)

if __name__ == '__main__':
    p = Publisher(url, env)
    c = Consumer(url, p, env)
    while True:
        try:
            c.consume()
        except ChannelWrongStateError as cc:
            logging.debug(f'Channel has closed stopping consumer: {cc}')
            exit(0)
