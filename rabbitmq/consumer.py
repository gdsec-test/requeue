from pika import BlockingConnection, SSLOptions, connection, credentials
import ssl
import logging


class Consumer:
    def __init__(self, host, port, vhost, user, password, publisher):
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

    def connect(self):
        if not self._connection:
            self._connection = BlockingConnection(self._params)
            self._channel = self._connection.channel()
            self._channel.exchange_declare('hashserve-dev-dlq', durable=True, internal=True)
            return self._channel

    def callback(self, ch, method, properties, body):
        logging.info(f'Consuming Messages from DLQ, Consumed: {body}')
        msg = body.decode("utf-8")
        print(self._channel.get_waiting_message_count)
        if self._channel.get_waiting_message_count() > 0:
            self.publisher.publish(msg)

    def consume(self):
        self._channel.basic_consume('hashserve-dev-dlq',
                                    on_message_callback=self.callback,
                                    auto_ack=True)
        self._channel.start_consuming()
