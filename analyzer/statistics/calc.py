from datetime import datetime as dt
from collections import Counter
import json
import logging
import sched
import time
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.INFO)


class StatsCalculator:
    def __init__(self, watcher):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._date_format = '%a, %d %b %Y %H:%M:%S %Z'
        self._watcher = watcher
        self._setup_scheduler()

    def _setup_scheduler(self):
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._scheduler.enter(delay=1, priority=1, action=self._fetch_and_analyze)
        self._scheduler.run()

    def _fetch_and_analyze(self):
        if not self._watcher.endpoint:
            self._logger.warning('There are no available endpoints at the moment')
        else:
            self._logger.info('Fetching data from endpoint %s' % self._watcher.endpoint)
            n = self._watcher.conf['last_n']
            url = 'http://%s/visits?n=%s' % (self._watcher.endpoint, n)
            visits = json.loads(urlopen(url).read().decode('utf-8'))
            if len(visits) > 0:
                stats = self._calc_statistics(visits)
                self._send_result(stats)
        delay = self._watcher.conf['repeat_seconds']
        self._scheduler.enter(delay=delay, priority=1, action=self._fetch_and_analyze)

    def _calc_statistics(self, requests):
        self._logger.info('Performing analysis on %s last visits...' % len(requests))
        num = len(requests)
        first_date = dt.strptime(requests[-1]['ts'], self._date_format)
        last_date = dt.strptime(requests[0]['ts'], self._date_format)
        timespan = int((last_date - first_date).total_seconds())
        top_country = Counter([req['country'] for req in requests]).most_common(1)[0][0]
        top_os = Counter([req['os'] for req in requests]).most_common(1)[0][0]
        top_browser = Counter([req['browser'] for req in requests]).most_common(1)[0][0]
        return {
            'num': num,
            'timespan': timespan,
            'top_country': top_country,
            'top_os': top_os,
            'top_browser': top_browser
        }

    def _send_result(self, stats):
        self._logger.info('Sending analysis results...')
        req = Request('http://%s/stats' % self._watcher.endpoint)
        databytes = json.dumps(stats).encode('utf-8')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Content-Length', len(databytes))
        urlopen(req, databytes)
