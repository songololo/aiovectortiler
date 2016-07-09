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
    def init_layer_recipes(cls, recipe_configs):
        with open(recipe_configs) as r_c:
            recipe = yaml.load(r_c.read())
            name = recipe_configs.split('/')[-1]
            cls.recipes[name] = Recipe(recipe)

'''
Plugins.load()
Plugins.hook('before_load', config=Configs)


def load_recipe(data):
    name = data.get('name', 'default')
    if name in RECIPES:
        raise ValueError('Recipe with name {} already exist'.format(name))
    data['name'] = name
    RECIPES[name] = Recipe(data)
    if len(RECIPES) == 1 and name != 'default':
        RECIPES['default'] = RECIPES[data['name']]


for recipe in Configs.layers:
    with Path(recipe).open() as f:
        load_recipe(yaml.load(f.read()))

Plugins.hook('load', config=config, recipes=RECIPES)
'''

class Recipe(dict):

    def __init__(self, data):
        super().__init__(data)
        self.load_layers(data['layers'])

    def load_layers(self, layers):
        self.layers = {}
        for layer in layers:
            self.layers[layer['name']] = Layer(self, layer)

    def __getattr__(self, attr):
        return self.get(attr, getattr(Configs.recipes, attr.upper(), None))

class Layer(dict):

    def __init__(self, recipe, layer_data):
        self.recipe = recipe
        super().__init__(layer_data)
        self.load_queries(layer_data['queries'])

    def load_queries(self, queries):
        self.queries = []
        for query in queries:
            self.queries.append(Query(self, query))

    def __getattr__(self, attr):
        return self.get(attr, getattr(self.recipe, attr))

    @property
    def id(self):
        return '{}:{}'.format(self.recipe.name, self.name)


class Query(dict):

    def __init__(self, layer, data):
        self.layer = layer
        super().__init__(data)

    def __getattr__(self, name):
        return self.get(name, getattr(self.layer, name))