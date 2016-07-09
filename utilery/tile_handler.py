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

    SQL_TEMPLATE = "SELECT {way}, * FROM ({sql}) AS data WHERE ST_IsValid(way) AND ST_Intersects(way, {bbox})"  # noqa
    GEOMETRY = "{way}"

    methods = ['GET']
    RADIUS = 6378137
    CIRCUM = 2 * math.pi * RADIUS
    SIZE = 256

    CONTENT = None
    CONTENT_TYPE = None

    def post_process(self):
        pass

    def serve(self, request):
        self.x = int(request.match_info['x'])
        self.y = int(request.match_info['y'])
        self.zoom = int(request.match_info['z'])
        self.layer = request.match_info['layer']
        try:
            self.recipe = request.match_info['recipe']
        except KeyError:
            self.recipe = Configs.server['default_recipe']

        print(self.x, self.y, self.zoom, self.layer, self.recipe)

        bounds = mercantile.bounds(self.x, self.y, self.zoom)
        self.west, self.south = mercantile.xy(bounds.west, bounds.south)
        self.east, self.north = mercantile.xy(bounds.east, bounds.north)

        if self.layer not in Configs.recipes[self.recipe].layers.values():
            logger.error('Layer {0} not found in recipe {1}'.format(self.layer, self.recipe))
            return aiohttp.errors.HttpBadRequest('Layer {0} not found in layer config file'.format(self.layer))
        else:
            self.process_layer()
            self.post_process()
            return self.CONTENT, 200, {"Content-Type": self.CONTENT_TYPE}

    def process_layer(self):
        layer_data = self.query_layer()
        self.add_layer_data(layer_data)

    def query_layer(self):
        features = []
        for query in self.layer.queries:
            if self.zoom < query.get('minzoom', 0) \
               or self.zoom > query.get('maxzoom', 22):
                continue
            sql = self.sql(query)
            try:
                rows = DB.fetchall(sql, dbname=query.dbname)
            except (psycopg2.ProgrammingError, psycopg2.InternalError) as e:
                msg = str(e)
                if Configs.server['debug']:
                    msg = "{} ** Query was: {}".format(msg, sql)
                    logger.error(msg)
            features += [self.to_feature(row, self.layer) for row in rows]
        return self.to_layer(self.layer, features)

    def sql(self, query):
        srid = query.srid
        bbox = 'ST_SetSRID(ST_MakeBox2D(ST_MakePoint({west}, {south}), ST_MakePoint({east}, {north})), {srid})'  # noqa
        bbox = bbox.format(west=self.west, south=self.south, east=self.east,
                           north=self.north, srid=srid)
        pixel_width = self.CIRCUM / (self.SIZE * query.scale) / 2 ** self.zoom
        if query.buffer:
            units = query.buffer * pixel_width
            bbox = 'ST_Expand({bbox}, {units})'.format(bbox=bbox, units=units)
        geometry = self.geometry
        if query.clip:
            geometry = geometry.format(way='ST_Intersection({way}, {bbox})')
        geometry = geometry.format(way='way', bbox=bbox)
        sql = query['sql'].replace('!bbox!', bbox)
        sql = sql.replace('!zoom!', str(self.zoom))
        sql = sql.replace('!pixel_width!', str(pixel_width))
        return self.SQL_TEMPLATE.format(way=geometry, sql=sql, bbox=bbox)

    def to_layer(self, layer, features):
        return {
            "name": layer['name'],
            "features": features
        }

    def add_layer_data(self, data):
        self.layer.append(data)

    def to_feature(self, row, layer):
        return {
            "geometry": self.process_geometry(row['_way']),
            "properties": self.row_to_dict(row)
        }

    def row_to_dict(self, row):
        def f(item):
            return not item[0].startswith('_') and item[0] != 'way'
        return dict(i for i in row.items() if f(i))

    def process_geometry(self, geometry):
        return geometry

    @property
    def geometry(self):
        return self.GEOMETRY


class ServePBF(ServeTile):

    endpoint = 'pbf'

    SCALE = 4096
    CONTENT_TYPE = 'application/x-protobuf'

    @property
    def geometry(self):
        return ('ST_AsText(ST_TransScale(%s, %.12f, %.12f, %.12f, %.12f)) as _way'  # noqa
                % (self.GEOMETRY, -self.west, -self.south,
                self.SCALE / (self.east - self.west),
                self.SCALE / (self.north - self.south)))

    def post_process(self):
        self.CONTENT = mapbox_vector_tile.encode(self.layer)


class ServeJSON(ServeTile):

    endpoint = 'json'

    GEOMETRY = "ST_AsGeoJSON(ST_Transform({way}, 4326)) as _way"  # noqa
    CONTENT_TYPE = 'application/json'

    def post_process(self):
        self.CONTENT = ujson.dumps(self.layer)

    def process_geometry(self, geometry):
        return ujson.loads(geometry)


class ServeGeoJSON(ServeJSON):

    endpoint = 'geojson'

    def to_layer(self, layer, features):
        return features

    def add_layer_data(self, data):
        self.layer.extend(data)

    def to_feature(self, row, layer):
        feature = super(ServeGeoJSON, self).to_feature(row, layer)
        feature["type"] = "Feature"
        feature['properties']['layer'] = layer['name']
        return feature

    def post_process(self):
        self.CONTENT = ujson.dumps({
            "type": "FeatureCollection",
            "features": self.layer
        })


class TileJson():

    endpoint = 'tilejson'

    def get(self):
        base = Configs.server['tilejson']
        base['vector_layers'] = []
        for recipe in RECIPES.values():
            for layer in recipe.layers.values():
                base['vector_layers'].append({
                    "description": layer.description,
                    "id": layer.id
                })
        return ujson.dumps(base)
