"""Module worker"""

import os
from typing import List
from loguru import logger
from api.client import YWH
from api.models import Program
from shared import setup_logger
from mq.client import MQClient
from mq.dto import MessageProgram

BASE_URL = "https://api.yeswehack.com"


def main():
    """main"""
    setup_logger()

    logger.info("Start")

    total = fetch_data()
    logger.info("programs count: {}", total)


def fetch_data() -> int:
    """fetch datas from api then publish"""

    api = YWH(base_url=BASE_URL)
    total = 0
    page = 1

    # from api.models import ProgramsResponse
    # with open("tests/resources/programs.json", "r", encoding="utf-8") as f:
    #     response = ProgramsResponse.model_validate_json(f.read())

    finished = False # do while
    while not finished:
        response = api.get_progams(page=page, results_per_page=20)

        publish(response.items)
        total += len(response.items)

        if response.pagination.page >= response.pagination.nb_pages:
            finished = True
        else:
            page = response.pagination.page + 1

    return total


def publish(data: List[Program]):
    """publish datas to the message queue"""
    host = os.environ.get("MQ_HOST", "localhost")
    queue_name = os.environ.get("MQ_QUEUE_NAME", "crawler")

    mq_client = MQClient(host=host)
    messages = [MessageProgram.model_validate(item.model_dump()) for item in data]

    with mq_client.channel(queue_name) as channel:
        for message in messages:
            channel.publish(message.model_dump_json())


if __name__ == "__main__":
    main()
