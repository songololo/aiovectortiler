import yaml


class Configs:

    server = None
    recipes = {}
    db_pool = None

    @classmethod
    def init_server_configs(cls, server_configs):
        with open(server_configs) as s_c:
            cls.server = yaml.load(s_c.read())

    @classmethod
    def init_layer_recipes(cls, layer_configs):
        with open(layer_configs) as l_c:
            recipe = yaml.load(l_c.read())
            name = recipe['name']
            layers = recipe['layers']
            cls.recipes[name] = layers