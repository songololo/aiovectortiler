import logging

logger = logging.getLogger(__name__)


class DB:
    app = None

    def __init__(cls, app):
        cls.app = app

    @classmethod
    async def fetchall(cls, query, geom_processor):
        features = []
        async with cls.app.pool.acquire() as db_connection:
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
