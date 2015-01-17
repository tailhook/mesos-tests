import random
import time
import requests


def wait_all_answer(urls, predicate=lambda x: True):
    urls = list(urls)
    while True:
        data = {}
        for u in urls:
            try:
                value = requests.get(u)
            except requests.exceptions.ConnectionError:
                time.sleep(0.1)
                break
            else:
                data[u] = value
                if not predicate(value):
                    time.sleep(0.1)
                    break
        else:
            print("DATA", data)
            return data

def wait_any_answer(urls, predicate=lambda x: True):
    while True:
        try:
            value = requests.get(random.choice(urls))
        except requests.exceptions.ConnectionError:
            pass
        else:
            if predicate(value):
                return value
        time.sleep(0.1)
