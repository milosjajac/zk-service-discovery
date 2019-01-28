import json
import logging
from kazoo.client import KazooClient, NoNodeError, NodeExistsError

logging.basicConfig(level=logging.INFO)

DATA_PARENT_NODE = '/services/visitor-data'
CONF_NODE = '/conf'


class ServiceWatcher:
    def __init__(self, hosts, timeout):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._endpoint = None
        self._conf = None
        self._zk = KazooClient(hosts=hosts)
        event = self._zk.start_async()
        event.wait(timeout=timeout)

        if self._zk.connected:
            self._logger.info('Kazoo client successfully connected')
            self._init_conf_node()
            self._setup_conf()
            self._setup_data_endpoint()
        else:
            self._zk.stop()
            self._logger.error('Kazoo client failed to connect')

    def _init_conf_node(self):
        default_conf = {
            'last_n': 100,
            'repeat_seconds': 30
        }
        conf_json = json.dumps(default_conf).encode('utf-8')
        try:
            self._zk.create(CONF_NODE, conf_json)
            self._logger.warning('No configuration found at path %s, setting default %s' % (CONF_NODE, conf_json))
        except NodeExistsError:
            pass

    def _setup_data_endpoint(self, event=None):
        self._zk.ensure_path(DATA_PARENT_NODE)
        endpoints = self._zk.get_children(DATA_PARENT_NODE, watch=self._setup_data_endpoint)
        if len(endpoints) == 0:
            self._logger.error('No available endpoints found')
        elif not self._endpoint or self._endpoint.split(':')[0] not in endpoints:
            self._logger.info('Found %s data service endpoints: %s' % (len(endpoints), endpoints))
            self._set_endpoint(endpoints[0])

    def _set_endpoint(self, endpoint, event=None):
        full_path = '%s/%s' % (DATA_PARENT_NODE, endpoint)
        data_bytes, stat = self._zk.get(full_path)
        data = json.loads(data_bytes.decode('utf-8'))
        self._endpoint = '%s:%s' % (endpoint, data['port'])
        self._logger.info('Endpoint set to %s, which is running since %s' % (self._endpoint, data['started']))

    @property
    def endpoint(self):
        return self._endpoint

    def _setup_conf(self, event=None):
            data_bytes, stat = self._zk.get(CONF_NODE, watch=self._setup_conf)
            self._conf = json.loads(data_bytes.decode('utf-8'))
            self._logger.info('New configuration found: %s' % self._conf)

    @property
    def conf(self):
        return self._conf
