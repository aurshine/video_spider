from typing import Union


class UrlSet:
    def __init__(self, init_url_data: Union[set, str, None], save_path):
        if init_url_data is None:
            init_url_data = set()

        if isinstance(init_url_data, set):
            self.urls = init_url_data
        elif isinstance(init_url_data, str):
            with open(init_url_data, 'r', encoding='utf-8') as f:
                self.urls = set(f.read().splitlines())
        else:
            raise TypeError("Invalid type for init_url_data")

        self.file = open(save_path, 'w', encoding='utf-8')
        self.save_path = save_path

    def add(self, url: str):
        url = url.strip()
        self.urls.add(url)
        self.file.write(url + '\n')

    def __contains__(self, item):
        return item in self.urls

    def __len__(self):
        return len(self.urls)

    def __iter__(self):
        return iter(self.urls)

    def __str__(self):
        return str(self.urls)

    def __del__(self):
        self.file.close()