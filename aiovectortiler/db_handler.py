import logging
import asyncpg

logger = logging.getLogger(__name__)

class DB(object):

    DEFAULT = "default"
    _ = {}

    @classmethod
    async def connect(cls, db_name, dsn_string):
        if db_name not in cls._:
            logger.info('adding database {0} at {1}'.format(db_name, dsn_string))
            try:
                cls._[db_name] = await asyncpg.create_pool(dsn_string, timeout=20, min_size=5, max_size=10)
            except TimeoutError as e:
                logger.error(e)
                raise TimeoutError(
                    '...unable to connect to db, timeout error, \
                    \n ...please check your DSN connection string, \
                    \n ...also remember that localhost connections require an IP address if connecting from within docker')
            except ConnectionRefusedError as e:
                logger.error(e)
                raise ConnectionRefusedError(
                    '...unable to connect to db, connection refused, \
                    \n ...please check your DSN connection string, \
                    \n ...also remember that localhost connections require an IP address if connecting from within docker')
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
            records = await db_connection.fetch(query, timeout=20)
            for record in records:
                    features.append({
                        'geometry': geom_processor(record['_way']),
                        'properties': cls.row_to_dict(record)
                    })
        return features

    @staticmethod
    def row_to_dict(record):
        return {key: value for key, value in record.items() if not key.startswith('_') and not key == 'way'}
