import os
import sys
import inspect
dir_current = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
dir_parent = os.path.dirname(dir_current)
sys.path.insert(0, dir_parent)

import sys
import logging
import argparse
import asyncpg

from sanic import Sanic
from sanic import response

import aiovectortiler
from aiovectortiler.config_handler import Configs
from aiovectortiler.db_handler import DB
from aiovectortiler.tile_handler import ServePBF, ServeGeoJSON, ServeJSON, TileJson


def serve_tiles(server_configs, layer_recipes, host, port):
    if not os.path.isfile(os.path.abspath(os.path.normpath(server_configs))):
        raise FileNotFoundError(('Server configuration file not found at {0}'.format(os.path.normpath(server_configs))))
    if not os.path.isdir(os.path.abspath(layer_recipes)):
        raise NotADirectoryError(('Layer recipes directory not found at {0}'.format(os.path.abspath(layer_recipes))))
    if not os.listdir(os.path.abspath(layer_recipes)):
        raise FileExistsError('Layer recipes directory is empty. Minimum 1 recipe is required.')

    # set the server configs
    Configs.init_server_configs(os.path.abspath(server_configs))

    # setup logging
    try:
        log_level = Configs.server['log_level'].upper()
    except KeyError:
        log_level = 'INFO'
    logging.basicConfig(stream=sys.stdout, level=log_level)
    logger = logging.getLogger(__name__)
    logger.info('STARTING ASYNCIO TILE SERVER APP')

    # set the layer configs
    for file in os.listdir(os.path.abspath(layer_recipes)):
        if file.endswith('.yaml') or file.endswith('.yml'):
            Configs.init_layer_recipes(os.path.join(os.path.abspath(layer_recipes), file))
    # check if a default recipe has been set in server configs. If so, set:
    try:
        default_recipe = Configs.server['default_recipe']
        if default_recipe[-4:] == '.yml':
            default_recipe = default_recipe[:-4]
        elif default_recipe[-5:] == '.yaml':
            default_recipe = default_recipe[:-5]
        Configs.recipes['default_recipe'] = Configs.recipes[default_recipe]
        Configs.recipes['default_recipe'].name = 'default_recipe_(same as {0})'.format(default_recipe)
        logger.info('Default recipe set to: {0}'.format(default_recipe))
    except KeyError:
        for first_recipe in Configs.recipes:
            logger.info('No default recipe set, using the first or only recipe as default: "{0}"'.format(first_recipe))
            Configs.recipes['default_recipe'] = Configs.recipes[first_recipe]
            break

    # create server app
    logger.info('Creating the server app')
    app = Sanic(__name__)

    # setup url routes and corresponding handlers
    app.add_route(ServePBF.serve, '/{layers}/{z}/{x}/{y}.pbf')
    app.add_route(ServePBF.serve, '/{recipe}/{layers}/{z}/{x}/{y}.pbf')
    app.add_route(ServePBF.serve, '/{layers}/{z}/{x}/{y}.mvt')
    app.add_route(ServePBF.serve, '/{recipe}/{layers}/{z}/{x}/{y}.mvt')

    app.add_route(ServeGeoJSON.serve, '/{layers}/{z}/{x}/{y}.geojson')
    app.add_route(ServeGeoJSON.serve, '/{recipe}/{layers}/{z}/{x}/{y}.geojson')

    app.add_route(ServeJSON.serve, '/{layers}/{z}/{x}/{y}.json')
    app.add_route(ServeJSON.serve, '/{recipe}/{layers}/{z}/{x}/{y}.json')

    @app.route('/tilejson/mvt.json')
    async def request_tilejson(request):
        content_type, body = TileJson.get()
        return response.text(body.encode(), content_type=content_type)

    # start the database pool
    logger.info('Creating the database pool')
    Configs.DB = DB(app)  # create the DB instance

    # use this approach to piggy-back the sanic uvloop event loop
    @app.listener('before_server_start')
    async def register_db(app, loop):
        app.pool = await asyncpg.create_pool(
            host=Configs.server['database']['host'],
            port=Configs.server['database']['port'],
            database=Configs.server['database']['database'],
            user=Configs.server['database']['user'],
            password=Configs.server['database']['password'],
            loop=loop)

if __name__ == '__main__':

    # parse arguments from command line
    ARGS = argparse.ArgumentParser(description="asyncio python tile server")
    ARGS.add_argument('--server_configs',
                      action="store",
                      dest='server_configs',
                      default='/configs/server_configs.yaml',
                      help='The YAML database config file')
    ARGS.add_argument('--layer_recipes',
                      action="store",
                      dest="layer_recipes",
                      default='/configs/layer_recipes/',
                      help='The YAML layers configs file')
    ARGS.add_argument('--host',
                      action="store",
                      dest="host",
                      default='0.0.0.0',
                      help='The host IP address')
    ARGS.add_argument('--port',
                      action="store",
                      dest="port",
                      default='80',
                      help='The host port')
    ARGS.add_argument('--version', action='version', version=aiovectortiler.VERSION)

    args = ARGS.parse_args()

    serve_tiles(args.server_configs, args.layer_recipes, args.host, args.port)