import pprint
import time
import logging
from testlib import restlib
from testlib.mesos import MesosMasters
from testlib.marathon import Marathons
from testlib import logging as _logging


INSTANCES = 1

log = logging.getLogger()

log.info("Starting")
mesos = MesosMasters(['mesos-master1', 'mesos-master2', 'mesos-master3'])
marathons = Marathons(['marathon1', 'marathon2', 'marathon3'])
marathons.wait_all_accessible()
mesos.wait_all_accessible()
log.info("Mesos masters are ok")
marathons.wait_all_accessible()
log.info("Marathons are ok")
leader = mesos.wait_start(slaves=3, frameworks=1)
log.info("Mesos slaves are ok. Leader is %s", leader)

marathons.start('webfsd -F -p $PORT -R /tmp/srv', instances=INSTANCES)
hostport_pairs = marathons.find_app('webfs', instances=INSTANCES)
log.info("All webfs tasks are started: %r", hostport_pairs)
restlib.wait_all_answer(
    'http://{}:{}/hostname'.format(host, port)
    for host, port in hostport_pairs)
log.info("Webfs tasks are started started and accessible")
