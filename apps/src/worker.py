"""Module worker"""

import os
import time

from loguru import logger
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import TypeAdapter, ValidationError
from pika import BlockingConnection
from pika import spec
from urllib3 import exceptions
from shared import setup_logger
from mq.client import MQClient
from mq.dto import MessageProgram


class Worker:
    """Worker"""

    mq_client: MQClient
    db_client: influxdb_client.InfluxDBClient
    db_bucket: str
    db_org: str

    def __init__(
        self,
        mq_host: str,
        tsdb_host: str,
        tsdb_token: str,
        tsdb_org: str,
        tsdb_bucket: str,
        tsdb_debug: bool = False,
    ):
        self.mq_client = MQClient(host=mq_host)
        self.db_client = influxdb_client.InfluxDBClient(
            url=tsdb_host,
            token=tsdb_token,
            org=tsdb_org,
            debug=tsdb_debug,
        )
        self.db_bucket = tsdb_bucket
        self.db_org = tsdb_org

    def start_consuming(self, queue_name: str):
        """start consuming message from the queue : blocking method"""
        with self.mq_client.channel(queue_name) as channel:
            channel.start_consuming(queue_name, callback=self.__mq_received)

    def __mq_received(
        self,
        channel: BlockingConnection,
        method: spec.Basic.Deliver,
        _properties: spec.BasicProperties,
        body: bytes,
    ):
        try:
            message = TypeAdapter(MessageProgram).validate_json(body)
            logger.debug("[MQ] Received #{}", message.slug)

            self.__store_message(message)

            logger.debug("[MQ] Ack #{}", message.slug)
            channel.basic_ack(delivery_tag=method.delivery_tag)

        except ValidationError:
            logger.error("[MQ] NAck #{}", body.decode())
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except exceptions.NewConnectionError as e:
            logger.error("[DB] connection error: {}", e)
            logger.debug("[MQ] NAck #{}", message.slug)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(5)

    def __store_message(self, message: MessageProgram):
        with self.db_client.write_api(write_options=SYNCHRONOUS) as write_api:
            point = (
                influxdb_client.Point("record")
                .tag("slug", message.slug)
                .field("reports_count", message.reports_count)
                .time(message.timestamp)
            )

            write_api.write(bucket=self.db_bucket, org=self.db_org, record=point)


def main():
    """main"""
    setup_logger()

    logger.debug("Read env value")
    queue_name = os.environ.get("MQ_QUEUE_NAME", "my-queue")
    mq_host = os.environ.get("MQ_HOST", "localhost")

    tsdb_host = os.environ.get("TSDB_HOST", "http://localhost:8086")
    tsdb_token = os.environ.get(
        "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", "my-super-secret-auth-token"
    )
    tsdb_org = os.environ.get("DOCKER_INFLUXDB_INIT_ORG", "my-org")
    tsdb_debug = TypeAdapter(bool).validate_python(
        os.environ.get("TSDB_DEBUG", "0")
    )
    tsdb_bucket = os.environ.get("DOCKER_INFLUXDB_INIT_BUCKET", "my-bucket")
    logger.info("Create worker [{}]", queue_name)
    worker = Worker(
        mq_host=mq_host,
        tsdb_host=tsdb_host,
        tsdb_token=tsdb_token,
        tsdb_org=tsdb_org,
        tsdb_bucket=tsdb_bucket,
        tsdb_debug=tsdb_debug,
    )

    logger.info("[MQ] start consuming [{}]", queue_name)
    worker.start_consuming(queue_name)


if __name__ == "__main__":
    main()
