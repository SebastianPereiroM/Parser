# -*- coding: utf-8 -*-

import urllib.parse as urlparse
import hashlib
from bs4 import BeautifulSoup

import common.Downloader as Downloader
import common.ModelConsts as Consts
from common.CityParser import CityParser


class VitebskParser(CityParser):

    def __init__(self):
        super().__init__()
        self._name = "Vitebsk"
        self._dir = "Vitebsk"
        self._main_page = "https://vitebsk.btrans.by/"

    def get_city_name(self):
        return self._name

    def get_city_dir(self):
        return self._dir

    def get_locale_dict(self):
        return {Consts.LANG_RU: "Витебск"}

    def get_transport_type_transport_reprs_map(self):
        page = Downloader.get_content(self._main_page)
        page_soup = BeautifulSoup(page, 'html.parser')
        divs_by_transport_type = page_soup.select('div.honey_bus')
        bus_a_elems = divs_by_transport_type[0].select('a')
        trolleybus_a_elems = divs_by_transport_type[1].select('a')
        tram_a_elems = divs_by_transport_type[2].select('a')

        bus_urls = [urlparse.urljoin(self._main_page, elem['href']) for elem in bus_a_elems]
        trolleybus_urls = [urlparse.urljoin(self._main_page, elem['href']) for elem in trolleybus_a_elems]
        tram_urls = [urlparse.urljoin(self._main_page, elem['href']) for elem in tram_a_elems]

        return {Consts.TYPE_BUS: bus_urls, Consts.TYPE_TROLLEYBUS: trolleybus_urls, Consts.TYPE_TRAM: tram_urls}

    def parse_transport_info(self, url):
        page = Downloader.get_content(url)
        page_soup = BeautifulSoup(page, 'html.parser')
        name = page_soup.select('.breadcrumbs span')[0].text
        number = name.split()[1]
        routes = {}
        elems_with_routes = page_soup.select('.stops')
        for route_elem in elems_with_routes:
            route_name = route_elem.select('h2')[0].text
            stops_urls = []
            for a_elem in route_elem.select('a'):
                relative_url = a_elem['href']
                absolute_url = urlparse.urljoin(url, relative_url)
                stops_urls.append(absolute_url)

            routes[route_name] = stops_urls
        return {Consts.TRANSPORT_NUMBER: number, Consts.ROUTES: routes}

    def parse_stop_info(self, url):
        page = Downloader.get_content(url)
        page_soup = BeautifulSoup(page, 'html.parser')
        name = page_soup.select('div.tt.col-xs-12')[1].select('a')[0].text
        schedule_table = page_soup.select('table.hours_set')[0]
        hours_row_elem = schedule_table.select('tr.hours')[0]
        hours = list(map(lambda x: x.text.strip(), hours_row_elem.select('td')[1:]))
        workdays_minutes = schedule_table.select('tr.weekdays')
        if len(workdays_minutes) == 0:
            workdays_minutes = None
        else:
            workdays_minutes = list(map(lambda td: td.text.strip(), workdays_minutes[0].select('td')[1:]))
        holidays_minutes = schedule_table.select('tr.weekends')
        if len(holidays_minutes) == 0:
            holidays_minutes = None
        else:
            holidays_minutes = list(map(lambda td: td.text.strip(), holidays_minutes[0].select('td')[1:]))

        # in minutes
        holidays_time = []
        workdays_time = []
        for idx in range(len(hours)):
            hour = hours[idx]
            if workdays_minutes:
                for minute in workdays_minutes[idx].split():
                    workdays_time.append("{hour}:{minute}".format(hour=hour, minute=minute.strip()))
            if holidays_minutes:
                for minute in holidays_minutes[idx].split():
                    holidays_time.append("{hour}:{minute}".format(hour=hour, minute=minute.strip()))

        string_for_id = name + self.get_city_name()
        stop_id = hashlib.sha1(string_for_id.encode()).hexdigest()
        return {Consts.STOP_NAME: name,
                Consts.STOP_ID: stop_id,
                Consts.SCHEDULES_BY_DAY_TYPE: {
                    Consts.DAY_TYPE_WORKDAYS: {
                        Consts.SCHEDULE_TIMES: workdays_time,
                        Consts.SCHEDULE_ANNOTATIONS: {}},
                    Consts.DAY_TYPE_HOLIDAYS: {
                        Consts.SCHEDULE_TIMES: holidays_time,
                        Consts.SCHEDULE_ANNOTATIONS: {}}}
                }
