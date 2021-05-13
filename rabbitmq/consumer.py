import logging
import ssl
import json
from datetime import datetime, timedelta
from pika import BlockingConnection, SSLOptions, connection, credentials


class Consumer:
    def __init__(self, host, port, vhost, user, password, publisher, env):
        context = ssl.create_default_context()
        self._params = connection.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=vhost,
            credentials=credentials.PlainCredentials(user, password),
            ssl_options=SSLOptions(context, host))
        self._connection = None
        self._channel = None
        self.publisher = publisher
        self.env = env
        self.queue_len = None

    def connect(self):
        if not self._connection:
            self._connection = BlockingConnection(self._params)
            self._channel = self._connection.channel()
            self._channel.exchange_declare('hashserve-dev-dlq',
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
            logging.info(f'Consuming Messages from DLQ, consumed: {body}')
            msg = body.decode("utf-8")
            self.publisher.publish(msg)

    def consume(self):
        self._channel.basic_consume('hashserve-dev-dlq',
                                    on_message_callback=self.callback,
                                    auto_ack=True)
        self._channel.start_consuming()
