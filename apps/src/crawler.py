"""Module worker"""

import os
from typing import List
from loguru import logger
from api.client import YWHClient
from api.models import Program, ProgramsResponse
from shared import setup_logger
from mq.client import MQClient
from mq.dto import MessageProgram


class Crawler:
    """Crawler"""

    queue_name: str
    api_client: YWHClient
    mq_client: MQClient

    def __init__(self, base_url: str, queue_name: str, mq_host: str):
        self.api_client = YWHClient(base_url)
        self.queue_name = queue_name
        self.mq_client = MQClient(host=mq_host)

    def fetch_data(self, file: str = None) -> int:
        """fetch datas from api then publish"""

        total = 0
        page = 1

        finished = False  # do while
        while not finished:

            if file is None:
                response = self.api_client.get_programs(
                    page=page, results_per_page=20
                )

            else:
                with open(file=file, mode="r", encoding="utf-8") as f:
                    response = ProgramsResponse.model_validate_json(f.read())
                    finished = True

            self.publish(response.items)
            total += len(response.items)

            if response.pagination.page >= response.pagination.nb_pages:
                finished = True
            else:
                page = response.pagination.page + 1

        return total

    def publish(self, data: List[Program]):
        """publish datas to the message queue"""

        messages = [
            MessageProgram.model_validate(item.model_dump()) for item in data
        ]

        with self.mq_client.channel(self.queue_name) as channel:
            for message in messages:
                channel.publish(message.model_dump_json())


def main():
    """main"""
    setup_logger()

    logger.debug("Read env value")
    queue_name = os.environ.get("MQ_QUEUE_NAME", "my-queue")
    mq_host = os.environ.get("MQ_HOST", "localhost")
    base_url = os.environ.get("CRAWLER_BASE_URL", "https://api.yeswehack.com")
    file = os.environ.get("CRAWLER_READ_FILE", None)
    if file:
        logger.warning(
            "Input file defined. Fetching skipped. Input: {} ",
            file,
        )

    logger.info("Create crawler [{}]", queue_name)
    crawler = Crawler(base_url=base_url, queue_name=queue_name, mq_host=mq_host)
    total = crawler.fetch_data(file=file)
    logger.info("programs count: {}", total)


if __name__ == "__main__":
    main()
