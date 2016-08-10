import pytest

from aiohttp.test_utils import TestClient, loop_context
from aiohttp import web, request

from aiovectortiler.config_handler import Configs, Recipe
from aiovectortiler.plugin_handler import Plugins
from aiovectortiler.db_handler import DB
from aiovectortiler.serve import serve_tiles

from .utils import copy


class TestPlugin(object):

    def on_before_load(self, config):
        config.BEFORE_LOAD = True

    def on_load(self, config, recipes):
        assert config.BEFORE_LOAD
        config.LOAD = True


def pytest_configure(config):
    Configs.DB = DB
    Configs.plugins = Plugins
    Configs.plugins.register_plugin(TestPlugin)
    Configs.recipes['default_recipe'] = Recipe({
        'name': 'default',
        'layers': [{
            'name': 'mylayer',
            'queries': [
                {
                    'sql': 'SELECT geometry AS way, type, name FROM osm_landusages_gen0',  # noqa
                    'maxzoom': 9
                }
            ]
        }]
    })


def pytest_unconfigure(config):
    pass


@pytest.fixture
def fetchall(monkeypatch):

    def _(result, check=None):
        def func(*args, **kwargs):
            if check:
                check(*args, **kwargs)
            return result
        monkeypatch.setattr('Configs.DB.fetchall', func)

    return _


@pytest.fixture
def client():
    pass
    #return Client(serve_tiles, BaseResponse)


class MonkeyPatchWrapper(object):
    def __init__(self, monkeypatch, wrapped_object):
        super().__setattr__('monkeypatch', monkeypatch)
        super().__setattr__('wrapped_object', wrapped_object)

    def __getattr__(self, attr):
        return getattr(self.wrapped_object, attr)

    def __getitem__(self, item):
        return self.wrapped_object.get(item)

    def __setattr__(self, attr, value):
        self.monkeypatch.setattr(self.wrapped_object, attr, value,
                                 raising=False)

    def __setitem__(self, item, value):
        self.monkeypatch.setitem(self.wrapped_object, item, value)

    def __delattr__(self, attr):
        self.monkeypatch.delattr(self.wrapped_object, attr)

    def __delitem__(self, item):
        self.monkeypatch.delitem(self.wrapped_object, item)


@pytest.fixture
def recipes(monkeypatch):
    return MonkeyPatchWrapper(monkeypatch, Configs.recipes)


@pytest.fixture()
def config(monkeypatch):
    return MonkeyPatchWrapper(monkeypatch, Configs)


@pytest.fixture
def layer(recipes):
    recipe = Recipe(copy(recipes['default']))
    recipes['default'] = recipe
    layer = recipe.layers['mylayer']
    return layer


@pytest.fixture
def plugins(monkeypatch):
    # Reset plugins.
    monkeypatch.setattr(Plugins, '_registry', [])
    monkeypatch.setattr(Plugins, '_hooks', {})

    return lambda p: Plugins.register_plugin(p)
