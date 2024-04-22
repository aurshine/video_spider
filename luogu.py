import os
import json
import random
from typing import List, Union

import m3u8
import setting


def make_luogu_url(page, difficulty=None, tag=None, keyword=None):
    if page is None:
        page = 1
    if difficulty is None:
        difficulty = ''
    if tag is None:
        tag = ''
    if keyword is None:
        keyword = ''

    return f'https://www.luogu.com.cn/problem/list?page{page}&difficulty={difficulty}&tag={tag}&keyword={keyword}&_contentOnly=1'


def get_problems_data(page=None, difficulty=None, tag=None, keyword=None):
    print(f'page = {page} difficulty = {difficulty} tag = {tag} keyword = {keyword}')
    url = make_luogu_url(page, difficulty, tag, keyword)
    datas = json.loads(m3u8.request_text(url))
    return datas


def get_problem_list(page=None, difficulty=None, tag=None, keyword=None) -> List[dict]:
    return get_problems_data(page, difficulty, tag, keyword)['currentData']['problems']['result']


def get_problem_count(difficulty=None, tag=None, keyword=None):
    return get_problems_data(1, difficulty, tag, keyword)['currentData']['problems']['count']


def random_problem(difficulty: Union[int, tuple] = None, tag=None, keyword=None):
    if not isinstance(difficulty, int):
        difficulty = random.randint(difficulty[0], difficulty[1])

    page = (get_problem_count(difficulty, tag, keyword) + 49) // 50

    problem = random.choice(get_problem_list(random.randint(1, page), difficulty, tag, keyword))
    return f'https://www.luogu.com.cn/problem/{problem["pid"]}', problem['title']


def main():
    url, title = random_problem(difficulty=4, tag=None, keyword='字符串')

    print(f'title: {title}\n url: {url}')


if __name__ == '__main__':
    main()