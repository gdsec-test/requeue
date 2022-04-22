import json
import logging
from datetime import datetime

from pika import BlockingConnection, URLParameters


class Consumer:
    def __init__(self, url, publisher, env):
        urls = url.split(';')
        self.conns = []
        for node in urls:
            self.conns.append(URLParameters(node))
        self.publisher = publisher
        self.env = env
        self._connection = BlockingConnection(self.conns)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(f'hashserve-{self.env}-dlq',
                                       durable=True,
                                       internal=True)

    def callback(self, ch, method, properties, body):
        data = json.loads(body)
        now = datetime.utcnow()
        publish_time = data['publishTime']
        publish_time = datetime.strptime(publish_time, '%Y-%m-%dT%H:%M:%SZ')
        delta = now - publish_time
        if delta.days == 0:
            self._connection.close()
            self.publisher.close()
        else:
            logging.debug(f'Consuming Messages from DLQ, consumed: {body}')
            self.publisher.publish(body)

    def consume(self):
        self._channel.basic_consume(f'hashserve-{self.env}-dlq',
                                    on_message_callback=self.callback,
                                    auto_ack=True)
        self._channel.start_consuming()
