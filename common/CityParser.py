# -*- coding: utf-8 -*-

import abc
import time
import json
import os
from tqdm import tqdm

import common.ModelConsts as Consts
import common.Config as Config
import common.Validation as Validation

from common.Exceptions import ValidationException


class CityParser(object, metaclass=abc.ABCMeta):

    def __init__(self):
        self.all_stops_set = set()

    @abc.abstractmethod
    def get_city_name(self):
        raise NotImplementedError("Should return city name")

    @abc.abstractmethod
    def get_city_dir(self):
        raise NotImplementedError("Should return directory name, where output files will be saved")

    @abc.abstractmethod
    def get_locale_dict(self):
        raise NotImplementedError("Should return dict, where keys - lang prefix, value - name of city in this lang")

    @abc.abstractmethod
    def get_transport_type_transport_reprs_map(self):
        raise NotImplementedError("Should return dict: transport_type => list of transport type representations")

    @abc.abstractmethod
    def parse_transport_info(self, transport_representation):
        raise NotImplementedError("Should return dict: transport_number => routes array, where"
                                  "route is also dict: route_name => route_stops_urls")

    @abc.abstractmethod
    def parse_stop_info(self, stop_representation):
        raise NotImplementedError("Should return dict: stop_name, stop_id,"
                                  " schedules:{workdays_times, holidays_times and it's annotations")

    def _parse_transport_info_task_generator(self, transport_representations):
        for representation in transport_representations:
            # parsing transport info
            try:
                transport_info = self.parse_transport_info(representation)
            except Exception as e:
                import sys
                raise type(e)(str(e) + "\n Exception in parsing transport info").with_traceback(sys.exc_info()[2])

            routes = []
            for route_name, stop_representations in transport_info["routes"].items():
                # parsing stop info
                try:
                    stops_info = [self.parse_stop_info(stop_repr) for stop_repr in stop_representations]
                except Exception as e:
                    import sys
                    raise type(e)(str(e) + "\n Number={0}. RouteName={1}".format(
                        transport_info[Consts.TRANSPORT_NUMBER],
                        route_name)).with_traceback(sys.exc_info()[2])

                schedules = []
                for stop_info in stops_info:

                    stop_error_message_header = "Number={0}. RouteName={1}. StopName={2}".format(
                        transport_info[Consts.TRANSPORT_NUMBER],
                        route_name,
                        stop_info[Consts.STOP_NAME])

                    self.__class__._validate_stop_info(stop_info, stop_error_message_header)

                    schedules.append({Consts.STOP_ID: stop_info[Consts.STOP_ID],
                                      Consts.SCHEDULE: stop_info[Consts.SCHEDULES_BY_DAY_TYPE]})
                    # for debug
                    if stop_info.get(Consts.DEBUG_FLAG, False):
                        print(stop_error_message_header)
                        print("Debug data:")
                        print(stop_info[Consts.DEBUG_DATA])
                    # end debug

                    self.all_stops_set.add((stop_info[Consts.STOP_ID],
                                            stop_info[Consts.STOP_NAME]))
                routes.append({Consts.ROUTE_NAME: route_name,
                               Consts.SCHEDULES: schedules})

            transport_dict = {Consts.TRANSPORT_NUMBER: transport_info[Consts.TRANSPORT_NUMBER],
                              Consts.ROUTES: routes}

            transport_error_header = "Number={0}".format(transport_info[Consts.TRANSPORT_NUMBER])
            self.__class__._validate_transport_dict(transport_dict, transport_error_header)

            yield transport_dict

    @staticmethod
    def _validate_stop_info(stop_info, error_message_header):
        errors = Validation.validate_stop_info(stop_info)
        if len(errors) != 0:
            error_message = error_message_header + "\n" + "\n".join(errors)
            raise ValidationException(error_message)

    @staticmethod
    def _validate_transport_dict(transport_dict, error_message_header):
        errors = Validation.validate_transport_dict(transport_dict)
        if len(errors) != 0:
            error_message = error_message_header + "\n" + "\n".join(errors)
            raise ValidationException(error_message)

    def parse_and_save(self, listener=None, lock=None):

        if listener:
            listener.parsing_started(self.get_city_name)

        city_dir = Config.PARSED_SCHEDULES_DIR + os.sep + self.get_city_dir()
        if lock:
            lock.acquire()
        if not os.path.exists(city_dir):
            os.makedirs(city_dir)
        timestamp = int(time.time())
        timestamp_dir = city_dir + os.sep + str(timestamp)
        if not os.path.exists(timestamp_dir):
            os.makedirs(timestamp_dir)
        if lock:
            lock.release()

        city_transports_meta = {}
        for transport_type, transport_reprs in self.get_transport_type_transport_reprs_map().items():
            message = "Parsing {city} {type} info".format(city=self.get_city_name(), type=transport_type)
            transport_dicts = []

            if listener:
                task_id = self.get_city_name() + transport_type
                listener.parse_task_started(task_id,
                                            len(transport_reprs),
                                            bar_message=message)

                for transport in self._parse_transport_info_task_generator(transport_reprs):
                    listener.parse_task_update(task_id, 1)
                    transport_dicts.append(transport)

                listener.parse_task_finished(task_id)

            else:
                print(message)
                with tqdm(total=len(transport_reprs)) as progress_bar:
                    for transport in self._parse_transport_info_task_generator(transport_reprs):
                        transport_dicts.append(transport)
                        progress_bar.update(1)

            city_transports_numbers = []

            for transport in transport_dicts:
                city_transports_numbers.append(transport[Consts.TRANSPORT_NUMBER])
                transport[Consts.TYPE_NAME] = transport_type
                transport_type_dir = timestamp_dir + os.sep + transport_type
                if not os.path.exists(transport_type_dir):
                    os.makedirs(transport_type_dir)
                filename = transport_type_dir + os.sep + "{number}.json".format(
                    number=transport[Consts.TRANSPORT_NUMBER])
                transport_json_string = json.dumps(transport)
                with open(filename, 'w', encoding="utf-8") as file:
                    file.write(transport_json_string)
            city_transports_meta[transport_type] = city_transports_numbers

        all_stops_list = []
        for stop_id, stop_name in self.all_stops_set:
            all_stops_list.append({Consts.STOP_ID: stop_id,
                                   Consts.STOP_NAME: stop_name})

        stops_json_string = json.dumps(all_stops_list)
        with open(timestamp_dir + os.sep + "stops.json", "w", encoding="utf-8") as file:
            file.write(stops_json_string)

        city_json = {Consts.CITY_NAME: self.get_city_name(),
                     Consts.TIME: int(time.time()),
                     Consts.SCHEMA_VERSION: Consts.CURRENT_SCHEMA_VERSION,
                     Consts.LANG_NAMES: self.get_locale_dict(),
                     Consts.CITY_TRANSPORTS: city_transports_meta,
                     Consts.CITY_STOPS: "stops.json"}

        city_json_string = json.dumps(city_json)
        with open(timestamp_dir + os.sep + "city.json", "w", encoding="utf-8") as file:
            file.write(city_json_string)

        if listener:
            listener.parsing_finished(self.get_city_name())

