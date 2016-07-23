import logging
import time
import aiopg
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

from utilery.config_handler import Configs


class DB(object):

    DEFAULT = "default"
    _ = {}

    @classmethod
    async def connect(cls, db_name, dsn_string):
        if db_name not in cls._:
            cls._[db_name] = await aiopg.create_pool(dsn_string)
        # if this is the first entry and if the name is not default, create a link
        # so doing the first db becomes the default, unless overwritten later by subsequent db pool
        if len(cls._) == 1 and db_name != 'default':
            cls._['default'] = cls._[db_name]
        logger.info('database keys: {0}'.format(cls._.keys()))

    @classmethod
    async def fetchall(cls, query, geom_processor, db_name, args=None):
        if not db_name:
            db_name = 'default'
        features = []
        async with cls._[db_name].acquire() as db_connection:
            async with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                await cursor.execute(query)
                async for row in cursor:
                    features.append({
                        'geometry': geom_processor(row['_way']),
                        'properties': cls.row_to_dict(row)
                    })
        return features

    @staticmethod
    def row_to_dict(row):
        return {key:value for key, value in row.items() if not key.startswith('_') and not key == 'way'}