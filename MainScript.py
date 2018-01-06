# -*- coding: utf-8 -*-

import time
import logging
import os
import multiprocessing as mp
from collections import deque

from tqdm import tqdm

import common.ModelConsts as Consts
import common.Config as Config
import parsers as p

from common.MultiprocessParseListener import MultiprocessParseListener


class HlybokayeParserTest1(p.HlybokayeParser):

    def __init__(self):
        super().__init__() 

    def get_city_dir(self):
        return "HlybokayeTests1"

    def get_city_name(self):
        return "HlybokayeTests1"


class HlybokayeParserTest2(p.HlybokayeParser):

    def __init__(self):
        super().__init__() 

    def get_city_dir(self):
        return "HlybokayeTests2"

    def get_city_name(self):
        return "HlybokayeTests2"


class HlybokayeParserTest3(p.HlybokayeParser):

    def __init__(self):
        super().__init__() 

    def get_city_dir(self):
        return "HlybokayeTests3"

    def get_city_name(self):
        return "HlybokayeTests3"


class HlybokayeParserTest4(p.HlybokayeParser):

    def __init__(self):
        super().__init__() 

    def get_city_dir(self):
        return "HlybokayeTests4"

    def get_city_name(self):
        return "HlybokayeTests4"


def setup_and_get_logger():
    if not os.path.exists(Config.LOG_DIR):
        os.makedirs(Config.LOG_DIR)
    logger = logging.getLogger("MainScript")
    log_filename = Config.LOG_DIR + os.sep + "{name}.log".format(name=int(time.time()))
    handler = logging.FileHandler(log_filename)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


def single_process_production():
    logger = setup_and_get_logger()
    cities = [p.HlybokayeParser(), HlybokayeParserTest1(), HlybokayeParserTest2(),
              HlybokayeParserTest3(), HlybokayeParserTest4()]

    start_time = time.time()
    logger.info("Parsing {n} cities".format(n=len(cities)))
    for city_parser in cities:
        try:
            city_parser.parse_and_save()
        except:
            import traceback
            exception_string = traceback.format_exc()
            logger.error("### Exception in city {name} ###".format(name=city_parser.get_city_name()))
            logger.error(exception_string)

    end_time = time.time()
    parsing_time = end_time - start_time
    logger.info("Parsed with {seconds} sec".format(seconds=int(parsing_time)))


def multiprocess_production():
    logger = setup_and_get_logger()

    cities = [p.HlybokayeParser(), HlybokayeParserTest1(), HlybokayeParserTest2(),
              HlybokayeParserTest3(), HlybokayeParserTest4()]


    start_time = time.time()
    logger.info("Parsing {n} cities".format(n=len(cities)))

    queue = mp.Queue()
    tasks_deque = deque(cities)
    task_id_to_progress_bar = {}
    number_of_tasks = len(tasks_deque)
    number_of_consumers = 4
    with mp.Pool(processes=number_of_consumers) as pool:
        tasks_in_progress = 0
        while number_of_tasks != 0:
            while tasks_in_progress < number_of_consumers and len(tasks_deque) != 0:
                pool.apply_async(__process_task(queue, tasks_deque.pop()))
                tasks_in_progress += 1

            if _dispatch_event(queue.get(), task_id_to_progress_bar):
                tasks_in_progress -= 1
                number_of_tasks -= 1

    fix_progress_bar_newlines = "\n" * (len(cities) - 1)
    print(fix_progress_bar_newlines)
    
    end_time = time.time()
    parsing_time = end_time - start_time
    logger.info("Parsed with {seconds} sec".format(seconds=int(parsing_time)))


def __process_task(queue, city):
    listener = MultiprocessParseListener(queue)
    city.parse_and_save(listener)


def _dispatch_event(event_tuple, list_of_progress_bars):
    if event_tuple[0] == MultiprocessParseListener.STATE_PARSE_TASK_STARTED:
        task_id = event_tuple[1]
        max_progress = event_tuple[2]
        list_of_progress_bars[task_id] = tqdm(total=max_progress)
    elif event_tuple[0] == MultiprocessParseListener.STATE_PARSE_TASK_UPDATE:
        task_id = event_tuple[1]
        update_delta = event_tuple[2]
        list_of_progress_bars[task_id].update(update_delta)
    elif event_tuple[0] == MultiprocessParseListener.STATE_PARSE_FINISHED:
        return True

    return False


if __name__ == '__main__':
    TEST_RUN = True

    if TEST_RUN:
        multiprocess_production()
    else:
        single_process_production()
