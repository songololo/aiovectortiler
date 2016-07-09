import yaml

class Configs:

    server = None
    layers = None

    @classmethod
    def init_server_configs(cls, server_configs):
        print(server_configs)
        with open(server_configs) as s_c:
            cls.server = yaml.load(s_c.read())


    @classmethod
    def init_layer_configs(cls, layer_configs):
        print(layer_configs)
        with open(layer_configs) as l_c:
            cls.layers = yaml.load(l_c.read())