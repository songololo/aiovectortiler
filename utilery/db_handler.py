import atexit
import logging
import time
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

from utilery.config_handler import Configs


class DB(object):

    DEFAULT = "default"
    _ = {}

    @classmethod
    def connect(cls, dbname=None):
        dbname = dbname or cls.DEFAULT
        if dbname not in cls._:
            cls._[dbname] = psycopg2.connect(Configs.server['database_connection_string'])
        return cls._[dbname]

    @classmethod
    def fetchall(cls, query, args=None, dbname=None):
        before = time.time()
        cur = DB.connect(dbname).cursor(
                                cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        after = time.time()
        logger.debug('%s => %s\n%s', query, (after - before) * 1000, '*' * 40)
        return rv


def close_connections():
    logger.debug('Closing DB connections')
    for conn in DB._.values():
        conn.close()
atexit.register(close_connections)