# -*- coding: utf-8 -*-

import abc


class ParseListener(object, metaclass=abc.ABCMeta):

    def __init__(self):
        pass

    @abc.abstractmethod
    def parsing_started(self, city_name, **kwargs):
        raise NotImplementedError("")

    @abc.abstractmethod
    def parse_task_started(self, task_id, task_count, **kwargs):
        raise NotImplementedError("")

    @abc.abstractmethod
    def parse_task_update(self, task_id, update_delta, **kwargs):
        raise NotImplementedError("")

    @abc.abstractmethod
    def parse_task_finished(self, task_id, **kwargs):
        raise NotImplementedError("")

    @abc.abstractmethod
    def parsing_finished(self, city_name, **kwargs):
        raise NotImplementedError("")
