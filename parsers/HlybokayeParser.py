# -*- coding: utf-8 -*-

import urllib.parse as urlparse
import hashlib
from bs4 import BeautifulSoup

import common.Downloader as Downloader
import common.ModelConsts as Consts
from common.CityParser import CityParser


class HlybokayeParser(CityParser):

    def __init__(self):
        super().__init__()
        self._name = "Hlybokaye"
        self._dir = "Hlybokaye"
        self._main_page = "https://rasp.kraj.by/"

    def get_city_name(self):
        return self._name

    def get_city_dir(self):
        return self._dir

    def get_locale_dict(self):
        return {Consts.LANG_RU: "Глубокое",
                Consts.LANG_BY: "Глыбокае",
                Consts.LANG_PO: "Głębokie"}

    def get_transport_type_transport_reprs_map(self):
        bus_url = "https://rasp.kraj.by/glubokoe/city-bus/route/"
        page = Downloader.get_content(bus_url)
        page_soup = BeautifulSoup(page, 'html5lib')
        divs_with_routes = page_soup.select_one('div#bus-list').select('p.column6')
        transport_number_to_routes_map = {}
        for div in divs_with_routes:
            a_elem = div.select_one('a')
            url = urlparse.urljoin(self._main_page, a_elem['href'])
            number = a_elem.select_one('b').text.strip().replace("№", "").split(" ")[0]
            route_name = a_elem.text.strip().split()[1:]
            route_name = " ".join(route_name)
            route_repr = RouteRepr(url, route_name)
            route_reprs = transport_number_to_routes_map.get(number, [])
            route_reprs.append(route_repr)
            transport_number_to_routes_map[number] = route_reprs

        transport_reprs = []
        for number, route_reprs in transport_number_to_routes_map.items():
            transport_reprs.append(TransportRepr(route_reprs, number))

        return {Consts.TYPE_BUS: transport_reprs}

    def parse_transport_info(self, representation):
        number = representation.number
        routes = {}
        for route_repr in representation.route_reprs:
            route_name = route_repr.name
            route_page = Downloader.get_content(route_repr.url)
            route_page_soap = BeautifulSoup(route_page, 'html5lib')
            stop_divs = route_page_soap.select("[id^='schedule-']")
            routes[route_name] = stop_divs
        return {Consts.TRANSPORT_NUMBER: number, Consts.ROUTES: routes}

    def parse_stop_info(self, div):
        name = div.select_one('h3').text.strip()
        debug = False
        debug_data = ""
        day_type_to_time_list_dict = {}
        for div_with_day_type in div.select("div.rasp-row-bus"):
            daytype_text = div_with_day_type.select_one('h4').text.strip()
            daytype = self.get_day_type_string(daytype_text)
            times = []
            annotations = {}
            has_annotation = False
            for span in div_with_day_type.select("span"):
                time_text = span.text.strip()
                time = time_text[:-2] + ":" + time_text[-2:]

                if span.attrs.get("style", None):
                    time += "*"
                    has_annotation = True
                times.append(time)
            if has_annotation:
                annotations["*"] = div_with_day_type.select_one("div.note").text.replace("—", "").strip()

            day_type_to_time_list_dict[daytype] = {Consts.SCHEDULE_TIMES: times,
                                                   Consts.SCHEDULE_ANNOTATIONS: annotations}
        string_for_id = name + self.get_city_name()
        stop_id = hashlib.sha1(string_for_id.encode()).hexdigest()
        return {Consts.STOP_NAME: name,
                Consts.STOP_ID: stop_id,
                Consts.SCHEDULES_BY_DAY_TYPE: day_type_to_time_list_dict,
                Consts.DEBUG_FLAG: debug,
                Consts.DEBUG_DATA: debug_data}

    def get_day_type_string(self, text):
        if text == 'будни':
            return Consts.DAY_TYPE_WORKDAYS
        elif text == 'пятница':
            return Consts.DAY_TYPE_FRIDAY
        elif text == 'суббота':
            return Consts.DAY_TYPE_SATURDAY
        elif text == 'воскресенье':
            return Consts.DAY_TYPE_SUNDAY
        elif text == 'выходные':
            return Consts.DAY_TYPE_HOLIDAYS
        else:
            raise RuntimeError("Unknown daytype {text}".format(text=text))


class TransportRepr:

    def __init__(self, list_of_route_reprs, number):
        self.route_reprs = list_of_route_reprs
        self.number = number


class RouteRepr:

    def __init__(self, route_url, route_name):
        self.url = route_url
        self.name = route_name




