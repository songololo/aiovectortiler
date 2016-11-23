import os
import yaml
import logging

logger = logging.getLogger(__name__)

class Configs:

    server = None
    recipes = {}
    DB = None
    plugins = None

    @classmethod
    def init_server_configs(cls, server_configs):
        with open(server_configs) as s_c:
            cls.server = yaml.load(s_c.read())

    @classmethod
    def init_layer_recipes(cls, recipe_configs):
        recipe_name = None
        if '/' in recipe_configs:
            recipe_name = os.path.normpath(recipe_configs).split('/')[-1]
        # for windows
        elif '\\' in recipe_configs:
            recipe_name = os.path.normpath(recipe_configs).split('\\')[-1]
        if recipe_name[-4:] == '.yml':
            recipe_name = recipe_name[:-4]
        elif recipe_name[-5:] == '.yaml':
            recipe_name = recipe_name[:-5]
        else:
            raise FileExistsError('File in layer recipes folder does not have a YAML extension: {0}'.format(recipe_configs))
        with open(recipe_configs) as r_c:
            load_recipe = yaml.load(r_c.read())
            cls.recipes[recipe_name] = Recipe(load_recipe)
            # add the recipe name based on the file name
            # this is needed by the tilejson query
            cls.recipes[recipe_name].name = recipe_name
            logger.info('Adding layer: {0}'.format(recipe_name))


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

# the following model structures for recipes / layers / queries allows searching up the chain
# for attributes. If not found in the root recipes level then it will check the server configs.
class Recipe(dict):

    def __init__(self, data):
        super().__init__(data)
        self.load_layers(data['layers'])

    def load_layers(self, layers):
        self.layers = {}
        for layer in layers:
            self.layers[layer['name']] = Layer(self, layer)

    def __getattr__(self, attr):
        return self.get(attr, Configs.server.get(attr, None))


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
        return '{0}:{1}'.format(self.recipe.name, self.name)

    @property
    def description(self):
        return self.get('description', 'no description provided')


class Query(dict):

    def __init__(self, layer, data):
        self.layer = layer
        super().__init__(data)

    def __getattr__(self, attr):
        return self.get(attr, getattr(self.layer, attr))
