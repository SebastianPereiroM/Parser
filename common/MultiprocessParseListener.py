# -*- coding: utf-8 -*-

import os

from common.ParseListener import ParseListener


class MultiprocessParseListener(ParseListener):

    STATE_PARSE_STARTED = 1
    STATE_PARSE_TASK_STARTED = 2
    STATE_PARSE_TASK_UPDATE = 3
    STATE_PARSE_TASK_FINISHED = 4
    STATE_PARSE_FINISHED = 5

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def parsing_started(self, city_name, **kwargs):
        self.queue.put((self.__class__.STATE_PARSE_STARTED, city_name, os.getpid()))

    def parsing_finished(self, city_name, **kwargs):
        self.queue.put((self.__class__.STATE_PARSE_FINISHED, city_name, os.getpid()))

    def parse_task_started(self, task_id, task_count, **kwargs):
        self.queue.put((self.__class__.STATE_PARSE_TASK_STARTED, task_id, task_count))

    def parse_task_update(self, task_id, update_delta, **kwargs):
        self.queue.put((self.__class__.STATE_PARSE_TASK_UPDATE, task_id, update_delta))

    def parse_task_finished(self, task_id, **kwargs):
        self.queue.put((self.__class__.STATE_PARSE_TASK_FINISHED, task_id))
