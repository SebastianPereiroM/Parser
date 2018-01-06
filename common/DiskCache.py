# -*- coding: utf-8 -*-

import os
import time
import common.Config as Config
import common.ConsoleProgress as Progress


class DiskCache:

    def __init__(self, cache_dir, expiration_time):

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        self.cache_dir = cache_dir
        self.files = {}
        filenames = [name for name in os.listdir(cache_dir) if os.path.isfile(cache_dir + os.sep + name)]
        for name in filenames:
            self.files[name] = os.path.getmtime(cache_dir + os.sep + name)

        self.expiration_time = expiration_time

    def __getitem__(self, url):
        filename = DiskCache.convert_url_to_filename(url)
        full_filename = self.cache_dir + os.sep + filename
        if filename in self.files:
            if time.time() - self.files[filename] < self.expiration_time:
                with open(full_filename, encoding='UTF-8') as file:
                    content = file.read()

                if content:
                    return content
                else:
                    return None

        return None

    def __setitem__(self, url, value):
        filename = DiskCache.convert_url_to_filename(url)
        full_filename = self.cache_dir + os.sep + filename
        with open(full_filename, 'w', encoding="UTF-8") as file:
            file.write(value)

        self.files[filename] = os.path.getmtime(full_filename)

    def clear(self, status_bar=True):
        total_count = len(self.files)
        count = 0
        if status_bar:
            print("Clear cache")
        for filename in self.files:
            full_filename = self.cache_dir + os.sep + filename
            os.remove(full_filename)
            count += 1
            if status_bar and count % 50 == 0:
                Progress.progress(count, total_count)

    @staticmethod
    def convert_url_to_filename(url):
        return url.replace("/", "_").replace(":", "_") + ".html"


cache = DiskCache(Config.HTML_CACHE_DIR, Config.CACHE_EXPIRE_TIME_SECONDS)
