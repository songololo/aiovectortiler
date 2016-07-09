from utilery.config_handler import Configs


class CORS(object):

    def on_response(self, response, request):
        if Configs.server['CORS']:
            response.headers["Access-Control-Allow-Origin"] = Configs.server['CORS']
            response.headers["Access-Control-Allow-Headers"] = "X-Requested-With"  # noqa