import os,sys,inspect
dir_current = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
dir_parent = os.path.dirname(dir_current)
sys.path.insert(0, dir_parent)

import sys
import logging
import argparse
import asyncio
from aiohttp import web
import aiohttp_cors

import utilery
from utilery.config_handler import Configs
from utilery.plugins import Plugins
from utilery.db_handler import DB
from utilery.tile_handler import ServePBF, ServeGeoJSON, ServeJSON, TileJson


# parse arguments from command line
ARGS = argparse.ArgumentParser(description="asyncio python tile server")
ARGS.add_argument('--server_configs',
                  action="store",
                  dest='server_configs',
                  default='../configs_server_example.yaml',
                  help='The YAML database config file')
ARGS.add_argument('--layer_recipes',
                  action="store",
                  dest="layer_recipes",
                  default='../layer_recipe_examples/',
                  help='The YAML layers configs file')
ARGS.add_argument('--host',
                  action="store",
                  dest="host",
                  default='0.0.0.0',
                  help='The host IP address')
ARGS.add_argument('--port',
                  action="store",
                  dest="port",
                  default=8080,
                  type=int,
                  help='The host port')
ARGS.add_argument('--version', action='version', version=utilery.VERSION)

args = ARGS.parse_args()


# set the server configs
Configs.init_server_configs(os.path.abspath(args.server_configs))


# setup logging
logging.basicConfig(stream=sys.stdout, level=Configs.server['log_level'].upper())
logger = logging.getLogger(__name__)
logger.info('STARTING ASYNCIO TILE SERVER APP')


# set the layer configs
for file in os.listdir(os.path.abspath(args.layer_recipes)):
    if file.endswith('.yaml') or file.endswith('.yml'):
        logger.info('Adding layer: {0}'.format(file))
        Configs.init_layer_recipes(os.path.join(os.path.abspath(args.layer_recipes), file))


# load plugins
logger.info('Loading plugins')
Plugins.load()


# create server app
logger.info('Creating the server app')
app = web.Application()

# setup url routes and corresponding handlers
async def request_pbf(request):
    content_type, body = await ServePBF.serve(request)
    return web.Response(content_type=content_type, body=body)
app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.pbf', request_pbf)
app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.pbf', request_pbf)
app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.mvt', request_pbf)
app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.mvt', request_pbf)

async def request_geojson(request):
    content_type, body = await ServeGeoJSON.serve(request)
    return web.Response(content_type=content_type, body=body.encode())
app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.geojson', request_geojson)
app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.geojson', request_geojson)

async def request_json(request):
    content_type, body = await ServeJSON.serve(request)
    return web.Response(content_type=content_type, body=body.encode())
app.router.add_route('GET', '/{layers}/{z}/{x}/{y}.json', request_json)
app.router.add_route('GET', '/{recipe}/{layers}/{z}/{x}/{y}.json', request_json)

async def request_tilejson(request):
    content_type, body = TileJson.get()
    return web.Response(content_type=content_type, body=body.encode())
app.router.add_route('GET', '/tilejson/mvt.json', request_tilejson)


# configure CORS TODO: look at how this interacts with plugin?
cors = aiohttp_cors.setup(app, defaults={
    Configs.server['CORS']: aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers='*',
        allow_headers='*'
    )
})
for route in list(app.router.routes()):
    cors.add(route)


# start the database pool
logger.info('Creating the database pool')
Configs.DB = DB()  # create the DB instance
loop = asyncio.get_event_loop()
for db_name, dsn_string in Configs.server['databases'].items():
    loop.run_until_complete(DB.connect(db_name, dsn_string)) # this is an awaitable async so use run_until_complete


# start the server
logger.info('Starting the server app at host: {0}, port: {1}'.format(args.host, args.port))
web.run_app(app, host=args.host, port=args.port)