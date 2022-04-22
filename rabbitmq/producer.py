import logging

from pika import BlockingConnection, URLParameters, exceptions


class Publisher:
    def __init__(self, url, env):
        urls = url.split(';')
        self.conns = []
        for node in urls:
            self.conns.append(URLParameters(node))
        self.env = env
        self._connection = BlockingConnection(self.conns)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(f'hashserve-{self.env}-dlq', durable=True, internal=True)

    def connect(self):
        if not self._connection:
            self._connection = BlockingConnection(self.conns)
            self._channel = self._connection.channel()
            self._channel.exchange_declare(f'hashserve-{self.env}-dlq', durable=True, internal=True)
            return self._channel

    def _publish(self, msg):
        logging.debug(f'Publishing message to hashserve: {msg}')
        self._channel.basic_publish(
            exchange='hashserve',
            routing_key=f'#.{self.env}',
            body=msg,
        )

    def publish(self, msg):
        try:
            self._publish(msg)
        except exceptions.ConnectionClosed:
            self.connect()
            self._publish(msg)

    def close(self):
        if self._connection and self._connection.is_open:
            self._connection.close()
