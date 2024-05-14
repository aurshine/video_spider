import os
from typing import Union
from multiprocessing import Lock as ProcessLock
from threading import Lock as ThreadLock


class UrlSet:
    def __init__(self, dir_path: str):
        """
        以一个文件夹的所有子文件夹名作为 url 集合

        :param dir_path: 文件夹路径
        """
        self.save_path = os.path.join(dir_path, 'download_urls')
        self.urls = set()

        if not os.path.exists(self.save_path):
            with open(self.save_path, 'w', encoding='utf-8'):
                pass
        else:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                for sub_dir in f.readlines():
                    self.urls.add(sub_dir.strip())

        self.process_lock = ProcessLock()
        self.thread_lock = ThreadLock()

    def add(self, url: str):
        with self.process_lock, self.thread_lock:
            url = str(url).strip()
            if url not in self.urls:
                self.urls.add(url)
                with open(self.save_path, 'a', encoding='utf-8') as f:
                    f.write(url + '\n')

    def __contains__(self, url: str):
        url = str(url).strip()
        return url in self.urls

    def __len__(self):
        return len(self.urls)

    def __iter__(self):
        return iter(self.urls)

    def __str__(self):
        return str(self.urls)