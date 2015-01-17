import json
import random
import pprint
import requests
from . import restlib



class Marathons(object):

    def __init__(self, hosts):
        self.hosts = hosts
        self.status_urls = list('http://{}:8080/v2/apps'.format(h)
                                for h in hosts)

    def wait_all_accessible(self):
        return restlib.wait_all_answer(self.status_urls)


    def start(self, cli, instances=1):
        host = random.choice(self.hosts)
        response = requests.post('http://{}:8080/v2/apps'.format(host),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'id': 'webfs',
                'cmd': 'exec '+cli,
                'cpus': 0.1,
                'mem': 128,
                'ports': [0],
                'instances': instances,
            }))
        assert response.status_code == 201, response

    def wait_app_instances(self, name, instances=1):
        response = restlib.wait_any_answer(
            ['http://{}:8080/v2/apps/{}'.format(host, name)
             for host in self.hosts],
            lambda resp: len(resp.json()['app']['tasks']) == instances)
        json = response.json()
        return [(task['host'], task['ports'][0])
                for task in json['app']['tasks']]

    def get_app_instances(self, name):
        response = restlib.wait_any_answer(
            ['http://{}:8080/v2/apps/{}'.format(host, name)
             for host in self.hosts])
        json = response.json()
        return [(task['host'], task['ports'][0])
                for task in json['app']['tasks']]
