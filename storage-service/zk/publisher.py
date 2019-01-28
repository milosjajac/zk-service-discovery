import datetime
import json
import logging
import socket
from kazoo.client import KazooClient

logging.basicConfig(level=logging.INFO)

PARENT_NODE = '/services/visitor-data'


class ServicePublisher:
    def __init__(self, hosts, timeout, publish_port):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._publish_port = publish_port
        self._zk = KazooClient(hosts=hosts)
        event = self._zk.start_async()
        event.wait(timeout=timeout)

        if self._zk.connected:
            self._logger.info('Kazoo client successfully connected')
            self._publish_status()
        else:
            self._zk.stop()
            self._logger.error('Kazoo client failed to connect')

    def _publish_status(self):
        full_path = '%s/%s' % (PARENT_NODE, socket.gethostname())
        data = {
            'started': str(datetime.datetime.now())[:19],
            'port': self._publish_port
        }
        json_data = json.dumps(data).encode(encoding='utf-8')
        self._logger.info('Publishing status %s to path %s' % (data, full_path))
        self._zk.create(full_path, json_data, ephemeral=True, makepath=True)
