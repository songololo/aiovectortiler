import os
import sys
import inspect
dir_current = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
dir_parent = os.path.dirname(dir_current)
sys.path.insert(0, dir_parent)

import sys
import logging
import argparse
import asyncio

if not sys.platform.startswith('win32') and not sys.platform.startswith('cygwin'):
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from aiohttp import web
import aiohttp_cors

import aiovectortiler
from aiovectortiler.config_handler import Configs
from aiovectortiler.plugin_handler import Plugins
from aiovectortiler.db_handler import DB
from aiovectortiler.tile_handler import ServePBF, ServeGeoJSON, ServeJSON, TileJson


def serve_tiles(server_configs, layer_recipes, host, port):
    if not os.path.isfile(os.path.abspath(os.path.normpath(server_configs))):
        raise FileNotFoundError('Server configuration file not found at {0}'.format(os.path.normpath(server_configs)))
    if not os.path.isdir(os.path.abspath(layer_recipes)):
        raise NotADirectoryError('Layer recipes directory not found at {0}'.format(os.path.abspath(layer_recipes)))
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

    # load plugins
    logger.info('Loading plugins')
    Configs.plugins = Plugins
    Configs.plugins.load(Configs.server)

    # TODO: develop and test some 'before_load' plugin hooks
    Configs.plugins.hook('before_load', config=Configs.server)

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
        logger.info('No default recipe set, using the first or only layer as default.')
        for first_key in Configs.recipes:
            Configs.recipes['default_recipe'] = Configs.recipes[first_key]
            break

    # TODO: develop and test some 'load' plugin hooks
    Configs.plugins.hook('load', config=Configs.server, recipes=Configs.recipes)

    # create server app
    logger.info('Creating the server app')
    app = web.Application()

    # setup url routes and corresponding handlers
    async def request_pbf(request):
        return await ServePBF.serve(request)
    app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.pbf', request_pbf)
    app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.pbf', request_pbf)
    app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.mvt', request_pbf)
    app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.mvt', request_pbf)

    async def request_geojson(request):
        return await ServeGeoJSON.serve(request)
    app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.geojson', request_geojson)
    app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.geojson', request_geojson)

    async def request_json(request):
        return await ServeJSON.serve(request)
    app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.json', request_json)
    app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.json', request_json)

    #TODO: confirm and test request_tilejson
    async def request_tilejson(request):
        content_type, body = TileJson.get()
        return web.Response(content_type=content_type, body=body.encode())
    app.router.add_route('GET', '/tilejson/mvt.json', request_tilejson)


    # configure CORS
    try:
        cors_config = Configs.server['CORS']
        logger.warning('CORS set to {0}'.format(cors_config))
    except KeyError:
        cors_config = '*'
        logger.warning('No CORS setting provided in server config file. Setting CORS to "*"')
    cors = aiohttp_cors.setup(app, defaults={
        cors_config: aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=cors_config,
            allow_headers=cors_config
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)


    # start the database pool
    logger.info('Creating the database pool')
    Configs.DB = DB  # create the DB instance
    loop = asyncio.get_event_loop()
    for db_name, dsn_string in Configs.server['databases'].items():
        loop.run_until_complete(Configs.DB.connect(db_name, dsn_string)) # this is an awaitable async so use run_until_complete

    # start the server
    logger.info('Starting the server app at host: {0}, port: {1}'.format(host, port))
    web.run_app(app, host=host, port=int(port))


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
                      default='8080',
                      help='The host port')
    ARGS.add_argument('--version', action='version', version=aiovectortiler.VERSION)

    args = ARGS.parse_args()

    serve_tiles(args.server_configs, args.layer_recipes, args.host, args.port)