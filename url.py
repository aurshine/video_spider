import os
from typing import Union
import threading
import atexit


class UrlSet:
    def __init__(self, init_url_data: Union[set, str, None], save_path):
        if init_url_data is None:
            init_url_data = set()

        if not os.path.exists(save_path):
            f = open(save_path, 'w', encoding='utf-8')
            f.close()

        if isinstance(init_url_data, set):
            self.urls = init_url_data
        elif isinstance(init_url_data, str):
            with open(init_url_data, 'r', encoding='utf-8') as f:
                self.urls = set(f.read().splitlines())
        else:
            raise TypeError("Invalid type for init_url_data")

        self.save_path = save_path
        self.lock = threading.Lock()

    def add(self, url: str):
        self.lock.acquire()
        try:
            if url not in self.urls:
                self.urls.add(url)
                with open(self.save_path, 'a', encoding='utf-8') as f:
                    f.write(url + '\n')
        finally:
            self.lock.release()

    def __contains__(self, item: str):
        return str(item).strip() in self.urls

    def __len__(self):
        return len(self.urls)

    def __iter__(self):
        return iter(self.urls)

    def __str__(self):
        return str(self.urls)