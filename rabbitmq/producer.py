import ssl
import json
import logging
from pika import BlockingConnection, SSLOptions, connection, credentials, exceptions


class Publisher:
    def __init__(self, host, port, vhost, user, password):
        context = ssl.create_default_context()
        self._params = connection.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=vhost,
            credentials=credentials.PlainCredentials(user, password),
            ssl_options=SSLOptions(context, host))
        self._connection = None
        self._channel = None

    def connect(self):
        if not self._connection:
            self._connection = BlockingConnection(self._params)
            self._channel = self._connection.channel()
            self._channel.exchange_declare('hashserve-dev-dlq', durable=True, internal=True)
            return self._channel

    def _publish(self, msg):
        logging.info(f'Publishing message to hashserve: {msg}')
        self._channel.basic_publish(
            exchange='hashserve',
            routing_key='#.dev',
            body=json.dumps(msg),
        )

    def publish(self, msg):
        try:
            self._publish(msg)
        except exceptions.ConnectionClosed:
            self.connect()
            self._publish(msg)
