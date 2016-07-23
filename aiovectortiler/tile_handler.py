import ujson
import math
import mercantile
import mapbox_vector_tile
import psycopg2
import logging

import aiohttp.errors
from utilery.config_handler import Configs

from utilery.db_handler import DB

logger = logging.getLogger(__name__)


class ServeTile():

    # parameters shared by all queries
    SQL_TEMPLATE = "SELECT {way}, * FROM ({sql}) AS data WHERE ST_IsValid(way) AND ST_Intersects(way, {bbox})"  # noqa
    GEOMETRY = "{way}"

    RADIUS = 6378137
    CIRCUM = 2 * math.pi * RADIUS
    SIZE = 256

    CONTENT = None
    CONTENT_TYPE = None

    @classmethod
    async def serve(cls, request):
        # fetch query parameters from request info
        x = int(request.match_info['x'])
        y = int(request.match_info['y'])
        zoom = int(request.match_info['z'])
        layers = request.match_info['layers']
        try:
            recipe_name = request.match_info['recipe']
        except KeyError:
            recipe_name = Configs.server['default_recipe']

        # check that recipe exists
        if recipe_name not in Configs.recipes.keys():
            logger.error('Recipe {0} not found in recipes'.format(recipe_name))
            return aiohttp.errors.HttpBadRequest('Recipe {0} not found in recipes'.format(recipe_name))

        # fetch recipe
        recipe = Configs.recipes[recipe_name]

        # extrapolate the layers
        if layers == 'all':
            layers = list(recipe.layers.keys())
        else:
            layers = layers.split('+')

        # compute bounds and extents
        bounds = mercantile.bounds(x, y, zoom)
        west, south = mercantile.xy(bounds.west, bounds.south)
        east, north = mercantile.xy(bounds.east, bounds.north)

        # process the layers
        layer_data = []
        for layer_name in layers:
            if layer_name not in recipe.layers.keys():
                logger.error('Layer {0} not found in recipe {1}'.format(layer_name, recipe_name))
                return aiohttp.errors.HttpBadRequest('Layer {0} not found in layer config file'.format(layer_name))
            else:
                layer = recipe.layers[layer_name]
                layer_data.append(await cls.query_layer(layer, zoom, west, south, east, north))
        return cls.post_process(layer_data)

    @classmethod
    async def query_layer(cls, layer, zoom, west, south, east, north):
        features = []
        for query in layer.queries:
            if zoom < query.get('minzoom', 0) \
               or zoom > query.get('maxzoom', 22):
                continue
            sql = cls.sql(query, zoom, west, south, east, north)
            db_name = query.db_name
            try:
                features = await Configs.DB.fetchall(sql, geom_processor=cls.geom_processor, db_name=db_name)
            except (psycopg2.ProgrammingError, psycopg2.InternalError) as e:
                msg = str(e)
                if Configs.server['debug']:
                    msg = "{} ** Query was: {}".format(msg, sql)
                    logger.error(msg)
        return {"name": layer['name'], "features": features}

    @classmethod
    def sql(cls, query, zoom, west, south, east, north):
        srid = query.srid
        bbox = 'ST_SetSRID(ST_MakeBox2D(ST_MakePoint({west}, {south}), ST_MakePoint({east}, {north})), {srid})'  # noqa
        bbox = bbox.format(west=west, south=south, east=east, north=north, srid=srid)
        pixel_width = cls.CIRCUM / (cls.SIZE * Configs.server['scale']) / 2 ** zoom
        if query.buffer:
            units = query.buffer * pixel_width
            bbox = 'ST_Expand({bbox}, {units})'.format(bbox=bbox, units=units)
        geometry = cls.geometry(west, south, east, north)
        if query.clip:
            geometry = geometry.format(way='ST_Intersection({way}, {bbox})')
        geometry = geometry.format(way='way')
        sql = query['sql'].replace('!bbox!', bbox)
        sql = sql.replace('!zoom!', str(zoom))
        sql = sql.replace('!pixel_width!', str(pixel_width))
        return cls.SQL_TEMPLATE.format(way=geometry, sql=sql, bbox=bbox)

    # overriden in children classes
    @classmethod
    def geometry(cls, west, south, east, north):
        pass

    # overriden in children classes
    @staticmethod
    def post_process(layer_data):
        pass

    @staticmethod
    def geom_processor(geometry):
        pass


class ServePBF(ServeTile):

    @classmethod
    def geometry(cls, west, south, east, north):
        return ('ST_AsText(ST_TransScale(%s, %.12f, %.12f, %.12f, %.12f)) as _way'  # noqa
                % (cls.GEOMETRY, -west, -south,
                   4096 / (east - west),
                   4096 / (north - south)))

    @staticmethod
    def geom_processor(geometry):
        return geometry

    @staticmethod
    def post_process(layer_data):
        response_content = mapbox_vector_tile.encode(layer_data)
        return 'application/x-protobuf', response_content


class ServeJSON(ServeTile):

    @classmethod
    def geometry(cls, west, south, east, north):
        return "ST_AsGeoJSON(ST_Transform({way}, 4326)) as _way"  # noqa

    @staticmethod
    def geom_processor(geometry):
        return ujson.loads(geometry)

    @staticmethod
    def post_process(layer_data):
        response_content = ujson.dumps(layer_data)
        return 'application/json', response_content


class ServeGeoJSON(ServeJSON):

    @staticmethod
    def post_process(layer_data):
        # TODO: should layers be flattened?
        for layer in layer_data:
            for feature in layer['features']:
                feature['type'] = 'Feature'
                #feature['properties']['layer'] = 'Layer_Name'  # TODO: sort out layer names
        response_content = ujson.dumps({
            "type": "FeatureCollection",
            "features": layer_data
        })
        return 'application/json', response_content


class TileJson():

    endpoint = 'tilejson'

    @staticmethod
    def get():
        base = ujson.loads(Configs.server['tileJSON_spec'])  #TODO: figure out
        base['vector_layers'] = []
        for recipe in Configs.recipes.values():
            for layer in recipe.layers.values():
                base['vector_layers'].append({
                    "description": layer.description,
                    "id": layer.id
                })
        return ujson.dumps(base)
