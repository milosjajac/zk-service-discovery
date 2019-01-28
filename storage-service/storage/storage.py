import MySQLdb
import MySQLdb.cursors


class Storage:
    def __init__(self, host, port, db, user, passwd):
        self._db = MySQLdb.connect(host=host, port=port, db=db, user=user, passwd=passwd,
                                   connect_timeout=10, cursorclass=MySQLdb.cursors.DictCursor)
        self._db.autocommit(True)

    def last_n_visits(self, n):
        with self._db.cursor() as cursor:
            cursor.execute("select * from visits order by ts desc limit %s" % n)
            return cursor.fetchall()

    def insert_statistics(self, stats):
        with self._db.cursor() as cursor:
            cursor.execute(
                "insert into stats (num, timespan, top_country, top_os, top_browser) values (%s, %s, %s, %s, %s)",
                (stats['num'], stats['timespan'], stats['top_country'], stats['top_os'], stats['top_browser'])
            )
