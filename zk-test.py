import os
import sys
import time
import socket
import datetime
import subprocess
import logging.config
import kazoo
from kazoo.client import KazooClient
from colorlog import ColoredFormatter


log = logging.getLogger()
IP_TO_NAME = {'172.18.0.1': 'zk1', '172.18.0.2': 'zk2', '172.18.0.3': 'zk3'}
counter = 0


def zk_states():
    states = {}
    for host in client.hosts:
        sock = socket.create_connection(host)
        sock.send(b'srvr')
        data = b''
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
        states[host[0]] = 'error'
        for line in data.split(b'\n'):
            try:
                k, v = line.split(b':', 1)
            except ValueError:
                continue
            else:
                if k == b'Mode':
                    states[host[0]] = v.decode('ascii').strip()
    return states


def get_leader(stable=False, seconds=60):
    for i in range(seconds):
        states = zk_states()
        leaders = [k for k, v in states.items() if v == 'leader']
        if len(leaders) != 1:
            time.sleep(1)
            continue
        if stable and not all(v in ('leader', 'follower')
                              for v in states.values()):
            time.sleep(1)
            continue
        break
    else:
        print("Zookeeper still instable", states)
    return IP_TO_NAME[leaders[0]]


def check_write(name=None, retries=20):
    global counter
    if name is None:
        cli = client
        name = '*' + current()
    else:
        cli = clients[name]
    log.info("Writing %s: %s -> %s", name, counter, counter+1)
    prev = str(counter).encode('ascii')
    for i in range(retries):
        try:
            data, _ = cli.get('/value')
        except (kazoo.exceptions.ConnectionLoss,
                kazoo.exceptions.SessionExpiredError) as e:
            log.error("Error reading from %s. Retrying (error: %r)", name, e)
            time.sleep(1)
        else:
            break
    else:
        log.error("Error reading from %s. Skipping...",name)
        return

    assert data == prev, "Value is wrong {} != {}".format(data, prev)
    for i in range(retries):
        try:
            cli.set('/value', str(counter+1).encode('ascii'))
        except (kazoo.exceptions.ConnectionLoss,
                kazoo.exceptions.SessionExpiredError) as e:
            log.error("Error writing to %s. Retrying (error: %r)", name, e)
            time.sleep(3)
            continue
        else:
            counter += 1
            if name.startswith('*'):
                name = '*' + current()
            log.info("Write to %s successful. Value: %d", name, counter)
            break
    else:
        log.error("Error writing to %s. Proceeding...",name)
        return

def current():
    return IP_TO_NAME[client._connection._socket.getpeername()[0]]


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {'()': 'colorlog.ColoredFormatter',
            'format': "%(asctime)s %(log_color)s %(message)s"},
        'debug': {'()': 'colorlog.ColoredFormatter',
            'format': "%(cyan)s%(asctime)s %(name)s %(message)s"},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'level': 'INFO',
            'stream': 'ext://sys.stdout',
        },
        'debug_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'debug',
            'level': 'CRITICAL',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'kazoo': {
            'handlers': ['debug_console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
})


clients = {name: KazooClient(ip) for ip, name in IP_TO_NAME.items()}
for _client in clients.values():
    _client.start()

client = KazooClient('172.18.0.1,172.18.0.2,172.18.0.3')
client.start()
client.create('/value', b'0')

leader = get_leader(True)
log.info("Leader %s we're connected to %s. Other hosts...", leader, current())
check_write('zk1')
check_write('zk2')
check_write('zk3')
log.info("All hosts are ok")

log.warning("Isolating leader %s", leader)
subprocess.check_call(["vagga_network", "isolate", leader])

check_write()
check_write('zk1')
check_write('zk2')

leader = get_leader()
log.info("Ok. Cluster works again. Leader %s we're connected to %s.",
    leader, current())

log.info("Checking isolated node")
check_write('zk3', retries=1)

log.info("Done, with %d successful writes", counter)
