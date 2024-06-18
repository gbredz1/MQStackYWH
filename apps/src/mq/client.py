"""Message Queue publisher"""

import contextlib

from pika import (
    BlockingConnection,
    ConnectionParameters,
    BasicProperties,
    DeliveryMode,
)
from pika.adapters.blocking_connection import BlockingChannel
from loguru import logger


class MQClient:
    """Connection wrapper"""

    parameters: ConnectionParameters

    def __init__(self, host: str):
        self.parameters = ConnectionParameters(host=host)

    @contextlib.contextmanager
    @logger.catch
    def channel(self, queue_name: str):
        """get channel"""
        connection = BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        try:
            yield MQChannel(channel=channel, routing_key=queue_name)

        finally:
            connection.close()


class MQChannel:
    """Channel wrapper"""

    channel: BlockingChannel
    routing_key: str

    def __init__(self, channel: BlockingChannel, routing_key: str):
        self.channel = channel
        self.routing_key = routing_key

    def publish(self, body: str | bytes, key: str = None):
        """publish with channel"""
        self.channel.basic_publish(
            exchange="",
            routing_key=self.routing_key if key is None else key,
            body=body,
            properties=BasicProperties(delivery_mode=DeliveryMode.Persistent),
        )

    def start_consuming(self, queue: str, callback):
        """consume message from queue"""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue, on_message_callback=callback)

        self.channel.start_consuming()

    def stop_consuming(self):
        self.channel.stop_consuming()
