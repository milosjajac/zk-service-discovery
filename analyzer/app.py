import os
from zk.watcher import ServiceWatcher
from statistics.calc import StatsCalculator

ZK_HOSTS = os.environ['ZK_HOSTS']

if __name__ == '__main__':
    service_watcher = ServiceWatcher(ZK_HOSTS, timeout=10)
    calc = StatsCalculator(service_watcher)
