import pprint
import requests
import logging
from functools import partial
from operator import methodcaller, itemgetter

from . import restlib


def _startup_predicate(slaves, frameworks, response):
    data = response.json()
    if data['leader'] != data['pid']:
        return True  # slaves have useless data, so kinda always ok
    return (data['activated_slaves'] == slaves and
            len(data['frameworks']) == frameworks)


class MesosMasters(object):

    def __init__(self, hosts):
        self.hosts = hosts
        self.status_urls = list('http://{}:5050/state.json'.format(h)
                                for h in hosts)

    def wait_all_accessible(self):
        restlib.wait_all_answer(self.status_urls)

    def wait_connected(self, slaves, frameworks):
        responses = restlib.wait_all_answer(self.status_urls,
            predicate=partial(_startup_predicate, slaves, frameworks))
        jsons = {k: v.json() for k, v in responses.items()}
        vals = list(map(itemgetter("leader"), jsons.values()))
        leader = vals[0]
        assert all(v == leader for v in vals), vals
        return leader
