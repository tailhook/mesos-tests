import datetime
import kazoo.client

cli = kazoo.client.KazooClient('172.18.0.1,172.18.0.2,172.18.0.3')
cli.start()
cli.create('/start_time', str(datetime.datetime.now()).encode())
value, stat = cli.get('/start_time')
print("Time", value.decode())
print("Stat", stat)
